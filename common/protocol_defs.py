"""
Definições compartilhadas do protocolo de comunicação CM5 <-> RP2040.
Espelho fiel de common/include/protocol_defs.h
"""

from enum import IntEnum

SOF_WORD = 0xAA55
SOF_MSB = 0xAA
SOF_LSB = 0x55


class MsgType(IntEnum):
    READ_REG = 0x01
    WRITE_REG = 0x02
    EXEC_CMD = 0x03
    READ_RESP = 0x81
    WRITE_ACK = 0x82
    CMD_ACK = 0x83
    TELEMETRY_STREAM = 0x90
    ERROR_NACK = 0xE0
    ASYNC_ALARM = 0xF0


class RegAddr(IntEnum):
    SYS_FW_VERSION = 0x00
    SYS_UPTIME_MS = 0x01
    SYS_STATE = 0x02
    SYS_FAULT_FLAGS = 0x03
    SYS_GPIO_STATUS = 0x04
    OPT_PHOTO_V = 0x10
    OPT_VDARK_V = 0x11
    OPT_CURRENT_UA = 0x12
    OPT_POWER_UW = 0x13
    OPT_LOS_THRESH_UA = 0x14
    CH_MODE = 0x20
    CH_BIAS_SET_V = 0x21
    CH_BIAS_MON_V = 0x22
    CH_DAC_CODE = 0x23
    CH_LIMIT_MIN_V = 0x24
    CH_LIMIT_MAX_V = 0x25
    DITHER_EN = 0x30
    DITHER_FREQ_HZ = 0x31
    DITHER_AMP_V = 0x32
    DITHER_PHASE_DEG = 0x33
    DEMOD_ERR_1F = 0x40
    DEMOD_ERR_2F = 0x41
    CTRL_KP = 0x50
    CTRL_KI = 0x51
    CTRL_KD = 0x52
    CTRL_SLEW_V_S = 0x53


class CmdId(IntEnum):
    ARM_RELAYS = 0x01
    DISARM_SAFE = 0x02
    CLEAR_FAULT = 0x03
    START_SWEEP = 0x04
    HOLD_FREEZE = 0x05
    CAL_DARK = 0x06
    DIAG_READ_MON = 0x07
    SET_SIM_MODE = 0x08
    ENTER_BOOTLOADER = 0x09


class SysState(IntEnum):
    INIT = 0
    IDLE_SAFE = 1
    PRE_ARM = 2
    ARMED_MANUAL = 3
    SWEEPING = 4
    TRACKING = 5
    HOLD = 6
    FAULT_LATCHED = 7
    MAINTENANCE = 8
