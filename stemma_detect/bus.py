from __future__ import annotations

import time


class I2CBus:
    """Small I2C interface exposed to sensor probes."""

    def __init__(self, bus_number: int = 1):
        try:
            from smbus2 import SMBus
        except ImportError as exc:
            raise RuntimeError("smbus2 is required to scan I2C") from exc

        self._bus = SMBus(bus_number)

    def close(self) -> None:
        self._bus.close()

    def __enter__(self) -> I2CBus:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def write_then_read(
        self,
        address: int,
        write: bytes,
        read_length: int,
        *,
        delay_ms: float = 0,
    ) -> bytes:
        from smbus2 import i2c_msg

        write_message = i2c_msg.write(address, write)
        read_message = i2c_msg.read(address, read_length)

        if delay_ms:
            self._bus.i2c_rdwr(write_message)
            time.sleep(delay_ms / 1000)
            self._bus.i2c_rdwr(read_message)
        else:
            self._bus.i2c_rdwr(write_message, read_message)

        return bytes(read_message)

    def read(self, address: int, length: int) -> bytes:
        from smbus2 import i2c_msg

        message = i2c_msg.read(address, length)
        self._bus.i2c_rdwr(message)
        return bytes(message)

    def write(self, address: int, data: bytes) -> None:
        from smbus2 import i2c_msg

        self._bus.i2c_rdwr(i2c_msg.write(address, data))

    def read_register(self, address: int, register: int, length: int) -> bytes:
        return self.write_then_read(address, bytes((register,)), length)
