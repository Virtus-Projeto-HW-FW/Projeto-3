#!/usr/bin/env python3
"""
Simple BIN to UF2 converter for Raspberry Pi Pico (RP2040).
Standard Microsoft UF2 format.
"""

import struct
import sys
from pathlib import Path

UF2_MAGIC_START0 = 0x0A324655
UF2_MAGIC_START1 = 0x9E5D5157
UF2_MAGIC_END = 0x0AB16414
UF2_FLAG_FAMILY_ID = 0x00002000
RP2040_FAMILY_ID = 0xE48BFF56
RP2040_FLASH_BASE = 0x10000000
CHUNK_SIZE = 256


def convert_bin_to_uf2(bin_path: Path, uf2_path: Path, base_addr: int = RP2040_FLASH_BASE) -> None:
    data = bin_path.read_bytes()
    num_blocks = (len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE
    out = bytearray()

    for block_no in range(num_blocks):
        chunk = data[block_no * CHUNK_SIZE : (block_no + 1) * CHUNK_SIZE]
        if len(chunk) < CHUNK_SIZE:
            chunk = chunk + b"\x00" * (CHUNK_SIZE - len(chunk))

        target_addr = base_addr + (block_no * CHUNK_SIZE)
        header = struct.pack(
            "<IIIIIIII",
            UF2_MAGIC_START0,
            UF2_MAGIC_START1,
            UF2_FLAG_FAMILY_ID,
            target_addr,
            CHUNK_SIZE,
            block_no,
            num_blocks,
            RP2040_FAMILY_ID,
        )
        data_block = chunk + b"\x00" * (476 - CHUNK_SIZE)
        footer = struct.pack("<I", UF2_MAGIC_END)
        out.extend(header + data_block + footer)

    uf2_path.write_bytes(out)
    print(f"UF2 gerado com sucesso em: {uf2_path} ({len(out)} bytes, {num_blocks} blocos).")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python bin2uf2.py <arquivo.bin> <arquivo.uf2>")
        sys.exit(1)
    convert_bin_to_uf2(Path(sys.argv[1]), Path(sys.argv[2]))
