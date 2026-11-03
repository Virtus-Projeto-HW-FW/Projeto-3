#ifndef PROTOCOL_DEFS_H
#define PROTOCOL_DEFS_H

#include <stdint.h>

#define SOF_WORD 0xAA55
#define SOF_MSB  0xAA
#define SOF_LSB  0x55

typedef enum {
    MSG_READ_REG         = 0x01,
    MSG_WRITE_REG        = 0x02,
    MSG_EXEC_CMD         = 0x03,
    MSG_READ_RESP        = 0x81,
    MSG_WRITE_ACK        = 0x82,
    MSG_CMD_ACK          = 0x83,
    MSG_TELEMETRY_STREAM = 0x90,
    MSG_ERROR_NACK       = 0xE0,
    MSG_ASYNC_ALARM      = 0xF0
} msg_type_t;

typedef enum {
    REG_SYS_FW_VERSION    = 0x00,
    REG_SYS_UPTIME_MS     = 0x01,
    REG_SYS_STATE         = 0x02,
    REG_SYS_FAULT_FLAGS   = 0x03,
    REG_SYS_GPIO_STATUS   = 0x04,
    REG_OPT_PHOTO_V       = 0x10,
    REG_OPT_VDARK_V       = 0x11,
    REG_OPT_CURRENT_UA    = 0x12,
    REG_OPT_POWER_UW      = 0x13,
    REG_OPT_LOS_THRESH_UA = 0x14,
    REG_CH_MODE           = 0x20,
    REG_CH_BIAS_SET_V     = 0x21,
    REG_CH_BIAS_MON_V     = 0x22,
    REG_CH_DAC_CODE       = 0x23,
    REG_CH_LIMIT_MIN_V    = 0x24,
    REG_CH_LIMIT_MAX_V    = 0x25,
    REG_DITHER_EN         = 0x30,
    REG_DITHER_FREQ_HZ    = 0x31,
    REG_DITHER_AMP_V      = 0x32,
    REG_DITHER_PHASE_DEG  = 0x33,
    REG_DEMOD_ERR_1F      = 0x40,
    REG_DEMOD_ERR_2F      = 0x41,
    REG_CTRL_KP           = 0x50,
    REG_CTRL_KI           = 0x51,
    REG_CTRL_KD           = 0x52,
    REG_CTRL_SLEW_V_S     = 0x53
} reg_addr_t;

typedef enum {
    CMD_ARM_RELAYS        = 0x01,
    CMD_DISARM_SAFE       = 0x02,
    CMD_CLEAR_FAULT       = 0x03,
    CMD_START_SWEEP       = 0x04,
    CMD_HOLD_FREEZE       = 0x05,
    CMD_CAL_DARK          = 0x06,
    CMD_DIAG_READ_MON     = 0x07,
    CMD_SET_SIM_MODE      = 0x08,
    CMD_ENTER_BOOTLOADER  = 0x09
} cmd_id_t;

typedef enum {
    SYS_STATE_INIT          = 0,
    SYS_STATE_IDLE_SAFE     = 1,
    SYS_STATE_PRE_ARM       = 2,
    SYS_STATE_ARMED_MANUAL  = 3,
    SYS_STATE_SWEEPING      = 4,
    SYS_STATE_TRACKING      = 5,
    SYS_STATE_HOLD          = 6,
    SYS_STATE_FAULT_LATCHED = 7,
    SYS_STATE_MAINTENANCE   = 8
} sys_state_t;

#endif /* PROTOCOL_DEFS_H */
