from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class I2CTransaction:
    """Bytes transferred by one successful probe bus operation."""

    address: int
    write: bytes | None = None
    read: bytes | None = None


class I2CBus:
    """Small I2C interface exposed to sensor probes."""

    def __init__(
        self,
        bus_number: int = 1,
        *,
        trace: Callable[[I2CTransaction], None] | None = None,
    ):
        try:
            from smbus2 import SMBus
        except ImportError as exc:
            raise RuntimeError("smbus2 is required to scan I2C") from exc

        self._bus = SMBus(bus_number)
        self._trace = trace

    def _record(self, transaction: I2CTransaction) -> None:
        if self._trace:
            self._trace(transaction)

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

        response = bytes(read_message)
        self._record(I2CTransaction(address, write=write, read=response))
        return response

    def read(self, address: int, length: int) -> bytes:
        from smbus2 import i2c_msg

        message = i2c_msg.read(address, length)
        self._bus.i2c_rdwr(message)
        response = bytes(message)
        self._record(I2CTransaction(address, read=response))
        return response

    def write(self, address: int, data: bytes) -> None:
        from smbus2 import i2c_msg

        self._bus.i2c_rdwr(i2c_msg.write(address, data))
        self._record(I2CTransaction(address, write=data))

    def read_register(self, address: int, register: int, length: int) -> bytes:
        return self.write_then_read(address, bytes((register,)), length)
