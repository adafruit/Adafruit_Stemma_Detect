from stemma_detect.result import Confidence
from stemma_detect.signature import DeviceSignature, exact

ADDRESSES = (0x6A, 0x6B)
DEFAULT_ADDRESSES = (0x6B,)
PACKAGE = "adafruit-circuitpython-lsm9ds1"
PROBE_CONFIDENCE = Confidence.MATCH

# WHO_AM_I_XG identifies the accelerometer/gyroscope half of the LSM9DS1.
SIGNATURE = DeviceSignature((exact("chip_id", 0x0F, b"\x68", show_value=True, weight=10),))
probe = SIGNATURE.probe
