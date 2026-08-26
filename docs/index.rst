Adafruit STEMMA Detect
======================

Adafruit STEMMA Detect identifies selected Adafruit STEMMA QT sensors on a Raspberry Pi and can install their CircuitPython drivers.

The project is intentionally curated. An I²C address alone is not treated as a definitive identity when multiple devices could respond at that address.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   api

Command line
------------

Scan I²C bus 1 without installing anything::

   stemma-scan --bus 1

Install drivers for definitive matches::

   stemma-scan --bus 1 --install

Prompt before installing drivers for possible matches::

   stemma-scan --bus 1 --install --prompt-possible-matches

Return a versioned, machine-readable scan report::

   stemma-scan --bus 1 --json
