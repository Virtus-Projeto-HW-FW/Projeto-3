import sys
from pathlib import Path

# Adiciona pasta common ao path
common_path = Path(__file__).resolve().parents[2] / "common"
sys.path.insert(0, str(common_path))

import protocol_defs


def test_sof_marker():
    assert protocol_defs.SOF_WORD == 0xAA55
    assert protocol_defs.SOF_MSB == 0xAA
    assert protocol_defs.SOF_LSB == 0x55


def test_message_types():
    assert protocol_defs.MsgType.READ_REG == 0x01
    assert protocol_defs.MsgType.WRITE_REG == 0x02
    assert protocol_defs.MsgType.EXEC_CMD == 0x03
    assert protocol_defs.MsgType.READ_RESP == 0x81
    assert protocol_defs.MsgType.WRITE_ACK == 0x82
    assert protocol_defs.MsgType.CMD_ACK == 0x83
    assert protocol_defs.MsgType.TELEMETRY_STREAM == 0x90
    assert protocol_defs.MsgType.ERROR_NACK == 0xE0
    assert protocol_defs.MsgType.ASYNC_ALARM == 0xF0


def test_cmd_ids():
    assert protocol_defs.CmdId.ARM_RELAYS == 0x01
    assert protocol_defs.CmdId.DISARM_SAFE == 0x02
    assert protocol_defs.CmdId.CLEAR_FAULT == 0x03
    assert protocol_defs.CmdId.START_SWEEP == 0x04
    assert protocol_defs.CmdId.HOLD_FREEZE == 0x05
    assert protocol_defs.CmdId.CAL_DARK == 0x06
    assert protocol_defs.CmdId.DIAG_READ_MON == 0x07
    assert protocol_defs.CmdId.SET_SIM_MODE == 0x08
    assert protocol_defs.CmdId.ENTER_BOOTLOADER == 0x09


def test_sys_states():
    assert protocol_defs.SysState.INIT == 0
    assert protocol_defs.SysState.IDLE_SAFE == 1
    assert protocol_defs.SysState.PRE_ARM == 2
    assert protocol_defs.SysState.ARMED_MANUAL == 3
    assert protocol_defs.SysState.SWEEPING == 4
    assert protocol_defs.SysState.TRACKING == 5
    assert protocol_defs.SysState.HOLD == 6
    assert protocol_defs.SysState.FAULT_LATCHED == 7
    assert protocol_defs.SysState.MAINTENANCE == 8
