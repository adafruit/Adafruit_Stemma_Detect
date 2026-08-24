from __future__ import annotations

import argparse
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version

from .bus import I2CBus
from .catalog import discover_chips
from .installer import install
from .result import Confidence
from .runtime import SHELL
from .scanner import Detection, scan


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
    prompt = f"Is the device at 0x{detection.address:02X} a {detection.name}?"
    try:
        return SHELL.prompt(prompt, default="n")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


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

    with I2CBus(args.bus) as bus:
        detections = scan(bus, chips)

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
