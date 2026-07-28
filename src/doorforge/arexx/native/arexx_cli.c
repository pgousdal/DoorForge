/**
 * arexx-cli — Minimal ARexx command-line client for ABBS.
 *
 * Uses the standard AmigaOS rexxsyslib.library to send an ARexx command
 * to an ABBS node port and print the result.
 *
 * Usage:
 *   arexx-cli <node> <command> [args...]
 *
 * Output format (stdout, machine-readable):
 *   RC:<integer>
 *   RESULT:<escaped-text>
 *   ERROR:<escaped-text>
 *
 * On success: RC line + RESULT line, exit 0.
 * On transport failure: ERROR line, exit 1.
 *
 * The RESULT and ERROR values are C-escaped: \n \\ \r are the only
 * escape sequences emitted.  The Python parser unescapes them.
 *
 * NOTE: no stdio integer formatting is used because this toolchain's
 * libgcc lacks __udivdi3/__umoddi3 helpers that newlib's printf needs.
 * All integer output is done with a simple utoa helper.
 */

#include <exec/types.h>
#include <exec/memory.h>
#include <exec/ports.h>
#include <dos/dos.h>

#include <rexx/rxslib.h>       /* RXSNAME, struct RxsLib */
#include <rexx/storage.h>      /* struct RexxMsg, RXCOMM, RXFF_* */
#include <rexx/rexxio.h>       /* I/O structures                */

#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/rexxsyslib.h>
#include <clib/alib_protos.h>  /* CreatePort, DeletePort        */

#include <stdlib.h>     /* atol */
#include <string.h>

#define BUF_SIZ 40


/* ---- library base (required by inline macros in proto/rexxsyslib.h) -- */

struct RxsLib *RexxSysBase = NULL;


/* ---- helpers --------------------------------------------------------- */

/* Simple unsigned long to string (no division from libgcc needed —
   the divisor 10 is a compile-time constant, so GCC emits a
   multiplicative magic-number sequence instead of __udivdi3). */
static char *ultoa(ULONG v, char *buf)
{
    char tmp[BUF_SIZ];
    int  i = 0;

    if (v == 0) { buf[0] = '0'; buf[1] = '\0'; return buf; }
    while (v) {
        tmp[i++] = '0' + (v % 10);
        v /= 10;
    }
    /* reverse into buf */
    {
        int j;
        for (j = 0; j < i; j++)
            buf[j] = tmp[i - 1 - j];
        buf[i] = '\0';
    }
    return buf;
}


/* Signed long to string. */
static char *ltoa(LONG v, char *buf)
{
    if (v < 0) {
        buf[0] = '-';
        ultoa((ULONG)(-(v + 1)) + 1UL, buf + 1);
    } else {
        ultoa((ULONG)v, buf);
    }
    return buf;
}


static void write_char(const char c)
{
    Write(Output(), (STRPTR)&c, 1L);
}


static void puts_escaped(const char *s)
{
    while (*s) {
        switch (*s) {
        case '\\':  PutStr("\\\\"); break;
        case '\n':  PutStr("\\n");  break;
        case '\r':  PutStr("\\r");  break;
        default:    write_char(*s); break;
        }
        s++;
    }
}


/* ---- resource ownership (see docs/reference/runtime.md) -------------- */
/*
 *  Resource          Creator          Owner        Release          Notes
 *  ────────────────  ───────────────  ───────────  ───────────────  ─────
 *  rexxsyslib.libr   OpenLibrary      main         CloseLibrary     global
 *  portname buffer   AllocMem         main         FreeMem          —
 *  destport ref      FindPort / ref   main         —                not owned
 *  replyport         CreatePort       main         DeletePort       —
 *  RexxMsg           CreateRexxMsg    main         DeleteRexxMsg    frees args
 *  argstrings        CreateArgstring  RexxMsg      DeleteRexxMsg    owned by msg
 */


int main(int argc, char *argv[])
{
    LONG               node;
    STRPTR             portname  = NULL;   /* owned, AllocMem          */
    struct MsgPort    *destport  = NULL;   /* borrowed from FindPort   */
    struct MsgPort    *replyport = NULL;   /* owned, CreatePort        */
    struct RexxMsg    *rxmsg     = NULL;   /* owned, CreateRexxMsg     */
    int                i;
    int                ret       = 0;

    /* ---- argument parsing ---- */
    if (argc < 3) {
        PutStr("ERROR:Usage: arexx-cli <node> <command> [args...]\n");
        return 1;
    }

    node = atol(argv[1]);
    if (node < 0) {
        PutStr("ERROR:node must be non-negative\n");
        return 1;
    }

    /* ---- open rexxsyslib.library (RXSNAME from rxslib.h) ---- */
    /* V33 = AmigaOS 2.04.  The inline macros reference RexXyBase
       directly, so we must store in the global variable. */
    RexxSysBase = (struct RxsLib *)OpenLibrary(RXSNAME, 33L);
    if (!RexxSysBase) {
        PutStr("ERROR:Failed to open rexxsyslib.library (version >= 33)\n");
        return 1;
    }

    /* ---- build port name: "ABBS node #<N> port" ---- */
    {
        char  nb[BUF_SIZ];
        int   len_nb;
        int   off;

        ultoa((ULONG)node, nb);
        len_nb = (int)strlen(nb);
        /* "ABBS node #" (11) + nb + " port" (5) + \0 (1) */
        portname = (STRPTR)AllocMem((ULONG)(11 + len_nb + 5 + 1), MEMF_CLEAR);
        if (!portname) {
            PutStr("ERROR:Out of memory (portname)\n");
            ret = 1;
            goto cleanup;
        }
        off = 0;
        CopyMem("ABBS node #", portname + off, 11);       off += 11;
        CopyMem(nb,           portname + off, len_nb);     off += len_nb;
        CopyMem(" port",      portname + off, 5);          /* +1 for \0 via MEMF_CLEAR */
    }

    /* ---- find the ABBS node port (DF-EVID-011) ---- */
    destport = FindPort(portname);
    if (!destport) {
        PutStr("ERROR:Port not found: ");
        puts_escaped(portname);
        PutStr("\n");
        ret = 1;
        goto cleanup;
    }

    /* ---- create reply port for ourselves ---- */
    replyport = CreatePort(NULL, 0);
    if (!replyport) {
        PutStr("ERROR:Failed to create reply port\n");
        ret = 1;
        goto cleanup;
    }

    /* ---- create the ARexx message ---- */
    rxmsg = CreateRexxMsg(replyport, NULL, portname);
    if (!rxmsg) {
        PutStr("ERROR:Failed to create ARexx message\n");
        ret = 1;
        goto cleanup;
    }

    /* ---- action code: command + request RESULT string ---- */
    rxmsg->rm_Action = RXCOMM | RXFF_RESULT;

    /* ---- populate argument strings (CreateArgstring, owned by RexxMsg) ---- */
    for (i = 2; i < argc && (i - 2) < MAXRMARG; i++) {
        UBYTE *arg = CreateArgstring(argv[i], strlen(argv[i]));
        if (arg) {
            rxmsg->rm_Args[i - 2] = arg;
        }
    }

    /* ---- send command and wait for reply ---- */
    /*
     * Standard Exec message passing:
     *   1. PutMsg  — delivers the message to the destination port
     *   2. WaitPort — blocks this task until a reply arrives
     *   3. GetMsg   — retrieves the replied message
     *
     * Limitation: WaitPort() blocks indefinitely if ABBS never replies.
     * There is no built-in timeout.  The Python subprocess timeout is the
     * only safeguard (default 30 s).  Killing the subprocess while a
     * message is outstanding may orphan the RexxMsg in ABBS's message
     * list, but does not leak resources on the helper side because
     * the OS will clean up on task exit.
     */
    PutMsg(destport, (struct Message *)rxmsg);
    WaitPort(replyport);
    rxmsg = (struct RexxMsg *)GetMsg(replyport);

    /* ---- extract results (rm_Result1 = RC, rm_Result2 = argstring) ---- */
    {
        char rcb[BUF_SIZ];
        LONG rc = rxmsg->rm_Result1;

        PutStr("RC:");
        ltoa(rc, rcb);
        PutStr(rcb);
        PutStr("\n");

        /* rm_Result2 is a pointer to the argstring, or 0. */
        UBYTE *res_arg = (UBYTE *)rxmsg->rm_Result2;
        PutStr("RESULT:");
        if (res_arg != NULL) {
            ULONG rlen = LengthArgstring(res_arg);
            ULONG j;
            for (j = 0; j < rlen; j++) {
                char c = (char)res_arg[j];
                switch (c) {
                case '\\': PutStr("\\\\"); break;
                case '\n': PutStr("\\n");  break;
                case '\r': PutStr("\\r");  break;
                default:   Write(Output(), (STRPTR)&c, 1L); break;
                }
            }
        }
        PutStr("\n");
    }

cleanup:
    /* Ownership rules:
     *   DeleteRexxMsg frees the RexxMsg itself plus all argstrings
     *   created with CreateArgstring (including Args[0..MAXRMARG-1]).
     *   DeletePort destroys the reply port.
     *   FreeMem releases the portname buffer.
     *   CloseLibrary closes rexxsyslib.library.
     *   The destport reference is borrowed — never freed.
     */
    if (rxmsg)     DeleteRexxMsg(rxmsg);
    if (replyport) DeletePort(replyport);
    if (portname)  FreeMem(portname, (ULONG)(strlen(portname) + 1));
    if (RexxSysBase) CloseLibrary((struct Library *)RexxSysBase);
    return ret;
}
