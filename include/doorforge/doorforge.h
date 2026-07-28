#ifndef DOORFORGE_DOORFORGE_H
#define DOORFORGE_DOORFORGE_H

/*
 * M0 PROVISIONAL HEADER
 *
 * This file documents the intended shape of the BBS-neutral API.
 * It is not ABI-stable and contains no claimed ABBS field mapping.
 *
 * Fields whose ABBS evidence is absent or ambiguous are marked with
 * explicit sentinel values or availability flags so that consumers
 * cannot confuse unavailable data with verified values.
 */

#ifdef __cplusplus
extern "C" {
#endif

typedef enum DFExitReason {
    DF_EXIT_NORMAL = 0,
    DF_EXIT_USER_QUIT,
    DF_EXIT_TIMEOUT,
    DF_EXIT_CARRIER_LOSS,
    DF_EXIT_CARRIER_LOSS_OR_TIMEOUT,
    DF_EXIT_BBS_SHUTDOWN,
    DF_EXIT_ADAPTER_ERROR,
    DF_EXIT_DOOR_FAILURE
} DFExitReason;

typedef struct DFSessionInfo {
    unsigned int node_number;
    unsigned int minutes_remaining;
    int is_local;
    int is_sysop;
    const char *display_name;

    /* Provisional: -1 means "unavailable" (no ABBS evidence). */
    long user_id;
    long security_level;
} DFSessionInfo;

#ifdef __cplusplus
}
#endif

#endif
