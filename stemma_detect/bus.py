from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Protocol, cast


@dataclass(frozen=True)
class I2CTransaction:
    """Bytes transferred by one successful probe bus operation."""

    address: int
    write: bytes | None = None
    read: bytes | None = None


class I2CBusProtocol(Protocol):
    """Minimal bus operations used by probes and topology adapters."""

    def write_then_read(
        self,
        address: int,
        write: bytes,
        read_length: int,
        *,
        delay_ms: float = 0,
    ) -> bytes: ...

    def read(self, address: int, length: int) -> bytes: ...

    def write(self, address: int, data: bytes) -> None: ...

    def read_register(self, address: int, register: int, length: int) -> bytes: ...


class BusioI2CProtocol(Protocol):
    """Subset of the Blinka ``busio.I2C`` API used by the adapter."""

    def try_lock(self) -> bool: ...

    def unlock(self) -> None: ...

    def readfrom_into(self, address: int, buffer: bytearray) -> None: ...

    def writeto(self, address: int, buffer: bytes) -> None: ...

    def writeto_then_readfrom(
        self,
        address: int,
        out_buffer: bytes,
        in_buffer: bytearray,
    ) -> None: ...


class BusioI2CAdapter:
    """Adapt a Blinka ``busio.I2C`` object for sensor probes."""

    def __init__(self, bus: BusioI2CProtocol):
        self._bus = bus

    @contextmanager
    def _locked(self) -> Iterator[None]:
        while not self._bus.try_lock():
            time.sleep(0.001)
        try:
            yield
        finally:
            self._bus.unlock()

    def write_then_read(
        self,
        address: int,
        write: bytes,
        read_length: int,
        *,
        delay_ms: float = 0,
    ) -> bytes:
        response = bytearray(read_length)
        with self._locked():
            if delay_ms:
                self._bus.writeto(address, write)
                time.sleep(delay_ms / 1000)
                self._bus.readfrom_into(address, response)
            else:
                self._bus.writeto_then_readfrom(address, write, response)
        return bytes(response)

    def read(self, address: int, length: int) -> bytes:
        response = bytearray(length)
        with self._locked():
            self._bus.readfrom_into(address, response)
        return bytes(response)

    def write(self, address: int, data: bytes) -> None:
        with self._locked():
            self._bus.writeto(address, data)

    def read_register(self, address: int, register: int, length: int) -> bytes:
        return self.write_then_read(address, bytes((register,)), length)


def adapt_i2c_bus(bus: I2CBusProtocol | BusioI2CProtocol) -> I2CBusProtocol:
    """Adapt a Blinka I²C bus, or return another duck-typed bus unchanged."""

    native_methods = ("read", "write", "read_register", "write_then_read")
    if all(callable(getattr(bus, method, None)) for method in native_methods):
        return cast(I2CBusProtocol, bus)

    busio_methods = (
        "try_lock",
        "unlock",
        "readfrom_into",
        "writeto",
        "writeto_then_readfrom",
    )
    if all(callable(getattr(bus, method, None)) for method in busio_methods):
        return BusioI2CAdapter(cast(BusioI2CProtocol, bus))

    return cast(I2CBusProtocol, bus)


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
