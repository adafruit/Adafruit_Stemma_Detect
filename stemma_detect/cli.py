from __future__ import annotations

import argparse
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version

from .bus import I2CBus, I2CTransaction
from .catalog import discover_chips
from .installer import install
from .result import Confidence
from .runtime import SHELL
from .scanner import Detection, ProbeDiagnostic, scan


def _arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect supported Adafruit STEMMA QT sensors",
    )
    parser.add_argument("--bus", type=int, default=1, help="Linux I2C bus number")
    parser.add_argument(
        "--install",
        action="store_true",
        help="install drivers for definitive matches",
    )
    parser.add_argument(
        "--prompt-possible-matches",
        action="store_true",
        help="prompt before installing drivers for possible matches",
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="show every probe result and I2C error",
    )
    args = parser.parse_args(argv)
    if args.prompt_possible_matches and not args.install:
        parser.error("--prompt-possible-matches requires --install")
    return args


def _installed_version(package: str) -> str | None:
    try:
        return version(package)
    except PackageNotFoundError:
        return None


def _confirm_possible(detection: Detection) -> bool:
    address_kind = detection.chip.address_kind(detection.address)
    address_note = f" ({address_kind} address)" if address_kind else ""
    prompt = f"Is the device at 0x{detection.address:02X}{address_note} a {detection.name}?"
    try:
        return SHELL.prompt(prompt, default="n")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def _print_diagnostic(diagnostic: ProbeDiagnostic) -> None:
    prefix = (
        f"PROBE: {diagnostic.chip.name} at 0x{diagnostic.address:02X} "
        f"[{diagnostic.chip.probe_risk.name.lower()}]"
    )
    if diagnostic.error is not None:
        if diagnostic.not_detected:
            print(f"{prefix}: NOT DETECTED")
            return
        print(f"{prefix}: ERROR: {type(diagnostic.error).__name__}: {diagnostic.error}")
        return

    if diagnostic.result is None:
        raise RuntimeError("probe diagnostic has neither a result nor an error")
    evidence = ", ".join(f"{key}={value}" for key, value in diagnostic.result.evidence.items())
    suffix = f": {evidence}" if evidence else ""
    print(f"{prefix}: {diagnostic.outcome.upper()}{suffix}")


def _print_transaction(transaction: I2CTransaction) -> None:
    fields = []
    if transaction.write is not None:
        fields.append(f"write={transaction.write.hex(' ').upper()}")
    if transaction.read is not None:
        fields.append(f"read={transaction.read.hex(' ').upper()}")
    print(f"I2C: 0x{transaction.address:02X} {' '.join(fields)}")


def _refine_possible_matches(
    detections: tuple[Detection, ...],
) -> tuple[tuple[Detection, ...], set[tuple[str, int]]]:
    refined = []
    confirmed = set()
    claimed_addresses = set()

    for detection in detections:
        if detection.result.confidence is not Confidence.POSSIBLE:
            refined.append(detection)
            continue
        if detection.address in claimed_addresses:
            continue
        if _confirm_possible(detection):
            refined.append(detection)
            confirmed.add((detection.chip.name, detection.address))
            claimed_addresses.add(detection.address)

    return tuple(refined), confirmed


def main() -> int:
    args = _arguments()
    chips = discover_chips()

    with I2CBus(
        args.bus,
        trace=_print_transaction if args.diagnostics else None,
    ) as bus:
        detections = scan(
            bus,
            chips,
            diagnostic=_print_diagnostic if args.diagnostics else None,
        )

    confirmed_possible = set()
    if args.install and args.prompt_possible_matches:
        detections, confirmed_possible = _refine_possible_matches(detections)

    if not detections:
        print("No supported Adafruit STEMMA QT sensors detected.")
        return 0

    for detection in detections:
        label = "MATCH" if detection.result.confidence is Confidence.MATCH else "POSSIBLE"
        print(f"{label}: {detection.name} at 0x{detection.address:02X}")
        if detection.result.evidence:
            evidence = ", ".join(
                f"{key}={value}" for key, value in detection.result.evidence.items()
            )
            print(f"  {evidence}")
        installed = _installed_version(detection.chip.package)
        if installed:
            print(f"  driver: {detection.chip.package} {installed} (installed)")
        else:
            print(f"  driver: {detection.chip.package} (not installed)")

    if args.install:
        for detection in detections:
            should_install = (
                detection.result.confidence is Confidence.MATCH
                or (
                    detection.chip.name,
                    detection.address,
                )
                in confirmed_possible
            )
            if should_install and _installed_version(detection.chip.package) is None:
                print(f"Installing: {detection.chip.package}")
                install(detection.chip)

    return 0
