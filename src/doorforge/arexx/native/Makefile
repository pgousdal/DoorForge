#
# Makefile for arexx-cli — native Amiga ARexx helper
#
# Supported compilers:
#   VBCC  — vbcc + vlink (recommended, tested)
#   GCC   — m68k-amigaos-gcc (cross or native)
#
# Output: arexx-cli (AmigaOS executable)
#

CC        = /opt/amiga/bin/m68k-amigaos-gcc
NDK      ?= /opt/amiga/m68k-amigaos/ndk-include
CFLAGS   ?= -O2 -I$(NDK) -Wall -Wno-pointer-sign
LDFLAGS  ?= -lamiga
TARGET   := arexx-cli

all: $(TARGET)

$(TARGET): arexx_cli.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

clean:
	-rm -f $(TARGET)
	-rm -f $(TARGET).o

.PHONY: all clean
