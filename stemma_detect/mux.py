from __future__ import annotations

from dataclasses import dataclass

from stemma_detect.bus import I2CBusProtocol

MUX_ADDRESSES = tuple(range(0x70, 0x78))


@dataclass(frozen=True)
class Multiplexer:
    """A conservatively identified PCA9546/PCA9548-compatible multiplexer."""

    address: int
    channels: int
    original_control: int
    path: tuple[MuxHop, ...] = ()

    @property
    def name(self) -> str:
        return "pca9546" if self.channels == 4 else "pca9548"

    def select(self, bus: I2CBusProtocol, channel: int) -> None:
        if not 0 <= channel < self.channels:
            raise ValueError("multiplexer channel is out of range")
        bus.write(self.address, bytes((1 << channel,)))

    def disable(self, bus: I2CBusProtocol) -> None:
        bus.write(self.address, b"\x00")

    def restore(self, bus: I2CBusProtocol) -> None:
        bus.write(self.address, bytes((self.original_control,)))


@dataclass(frozen=True)
class MuxHop:
    """One selected multiplexer channel in a detection path."""

    address: int
    channel: int


def probe_multiplexer(bus: I2CBusProtocol, address: int) -> Multiplexer | None:
    """Actively verify mux control-byte behavior and restore its original state."""

    original = bus.read(address, 1)
    if len(original) != 1 or (original[0] > 0x0F and original[0] not in (0x10, 0x20, 0x40, 0x80)):
        # A fresh four- or eight-channel mux normally has no channels selected.
        # Also permit one selected high channel on an eight-channel mux, while
        # restricting the initial value enough to avoid most unrelated devices.
        return None

    changed = False
    try:
        # Check multiple masks. A register-based sensor can coincidentally return
        # one expected byte after a one-byte write is treated as a register
        # pointer (BMP390 can do this at 0x77), but is very unlikely to echo this
        # complete mux-control sequence.
        for control in (0x01, 0x02, 0x03):
            bus.write(address, bytes((control,)))
            changed = True
            if bus.read(address, 1) != bytes((control,)):
                return None

        bus.write(address, b"\x10")
        high_channel = bus.read(address, 1)
        if high_channel == b"\x10":
            channels = 8
        elif high_channel == b"\x00":
            channels = 4
        else:
            return None
        return Multiplexer(address, channels, original[0])
    finally:
        if changed:
            bus.write(address, original)


def discover_multiplexers(
    bus: I2CBusProtocol,
    *,
    excluded_addresses: frozenset[int] = frozenset(),
) -> tuple[Multiplexer, ...]:
    """Find standard-address PCA9546/PCA9548-compatible muxes."""

    found = []
    for address in MUX_ADDRESSES:
        if address in excluded_addresses:
            continue
        try:
            mux = probe_multiplexer(bus, address)
        except (OSError, RuntimeError, ValueError):
            continue
        if mux is not None:
            found.append(mux)
    return tuple(found)
