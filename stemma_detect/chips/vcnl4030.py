from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x60,)
PACKAGE = "adafruit-circuitpython-vcnl4030"
PROBE_CONFIDENCE = Confidence.MATCH

SIGNATURE = DeviceSignature(
    (
        exact(
            "device_id",
            0x0E,
            b"\x80\x00",
            mask=b"\xff\x00",
            show_value=True,
            weight=10,
        ),
    )
)
probe = SIGNATURE.probe
