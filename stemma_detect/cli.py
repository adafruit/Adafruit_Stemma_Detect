from __future__ import annotations

import argparse
from collections.abc import Sequence

from .bus import I2CBus, I2CTransaction
from .installer import InstallOutcome, create_install_plan, driver_version, install_drivers
from .mux import MuxHop
from .result import Confidence
from .runtime import SHELL
from .scanner import Detection, ProbeDiagnostic, ScanReport, scan_all
from .serialization import report_to_json


def _path_text(path: tuple[MuxHop, ...]) -> str:
    return "".join(f" via mux 0x{hop.address:02X} channel {hop.channel}" for hop in path)


def _detection_key(detection: Detection) -> tuple[tuple[MuxHop, ...], int]:
    return detection.path, detection.address


def _confirmation_key(detection: Detection) -> tuple[str, tuple[MuxHop, ...], int]:
    return detection.chip.name, detection.path, detection.address


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
    parser.add_argument(
        "--json",
        action="store_true",
        help="write the scan report as machine-readable JSON",
    )
    args = parser.parse_args(argv)
    if args.prompt_possible_matches and not args.install:
        parser.error("--prompt-possible-matches requires --install")
    if args.json and args.install:
        parser.error("--json cannot be combined with --install")
    if args.json and args.diagnostics:
        parser.error("--json cannot be combined with --diagnostics")
    return args


def _confirm_possible(detection: Detection) -> bool:
    address_kind = detection.chip.address_kind(detection.address)
    address_note = f" ({address_kind} address)" if address_kind else ""
    path = _path_text(detection.path)
    prompt = (
        f"Is the device at 0x{detection.address:02X}{path}{address_note} "
        f"a {detection.name.upper()}?"
    )
    try:
        return SHELL.prompt(prompt, default="n")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def _print_diagnostic(diagnostic: ProbeDiagnostic) -> None:
    prefix = (
        f"PROBE: {diagnostic.chip.name.upper()} at 0x{diagnostic.address:02X}"
        f"{_path_text(diagnostic.path)} "
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
    if diagnostic.result.score is not None:
        score = f"score={diagnostic.result.score}/{diagnostic.result.max_score}"
        evidence = ", ".join(filter(None, (evidence, score)))
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
) -> tuple[
    tuple[Detection, ...],
    set[tuple[str, tuple[MuxHop, ...], int]],
]:
    refined = []
    confirmed = set()
    claimed_addresses = set()

    for detection in detections:
        if detection.result.confidence is not Confidence.POSSIBLE:
            refined.append(detection)
            continue
        detection_key = _detection_key(detection)
        if detection_key in claimed_addresses:
            continue
        if _confirm_possible(detection):
            refined.append(detection)
            confirmed.add(_confirmation_key(detection))
            claimed_addresses.add(detection_key)

    return tuple(refined), confirmed


def main() -> int:
    args = _arguments()
    with I2CBus(
        args.bus,
        trace=_print_transaction if args.diagnostics else None,
    ) as bus:
        report = scan_all(
            bus,
            diagnostic=_print_diagnostic if args.diagnostics else None,
        )
        detections = report.detections

    if args.json:
        print(report_to_json(report, bus=args.bus))
        return 0

    confirmed_possible = set()
    if args.install and args.prompt_possible_matches:
        detections, confirmed_possible = _refine_possible_matches(detections)

    for mux in report.multiplexers:
        print(
            f"MUX: {mux.name.upper()} at 0x{mux.address:02X}"
            f"{_path_text(mux.path)} ({mux.channels} channels)"
        )

    if not detections:
        print("No supported Adafruit STEMMA QT sensors detected.")
        return 0

    for detection in detections:
        label = "MATCH" if detection.result.confidence is Confidence.MATCH else "POSSIBLE"
        print(
            f"{label}: {detection.name.upper()} at 0x{detection.address:02X}"
            f"{_path_text(detection.path)}"
        )
        if detection.result.evidence or detection.result.score is not None:
            fields = [f"{key}={value}" for key, value in detection.result.evidence.items()]
            if detection.result.score is not None:
                fields.append(f"score={detection.result.score}/{detection.result.max_score}")
            print(f"  {', '.join(fields)}")
        installed = driver_version(detection.chip.package)
        if installed:
            print(f"  driver: {detection.chip.package} {installed} (installed)")
        else:
            print(f"  driver: {detection.chip.package} (not installed)")

    if args.install:
        plan = create_install_plan(
            ScanReport(detections, report.multiplexers),
            confirm_possible=lambda detection: _confirmation_key(detection) in confirmed_possible,
        )
        for item in plan:
            if not item.needs_install:
                continue
            print(f"Installing: {item.package}")
            result = install_drivers((item,))[0]
            if result.outcome is InstallOutcome.FAILED:
                raise RuntimeError(result.error)

    return 0
