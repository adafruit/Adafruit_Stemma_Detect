API reference
=============

Quick start
-----------

For a normal Raspberry Pi application, :func:`~stemma_detect.scanner.detect` owns the bus lifecycle
and uses the bundled catalog:

.. code-block:: python

   from stemma_detect import detect

   report = detect(1)
   for sensor in report.matches:
       print(sensor.name, sensor.address_hex, sensor.driver_package)

Possible matches are kept separate because their signatures are not strong enough for automatic
driver installation:

.. code-block:: python

   for sensor in report.possible_matches:
       print("Confirmation required:", sensor.name, sensor.evidence)

Use :func:`~stemma_detect.scanner.scan_all` when the application owns the bus or supplies another
:class:`~stemma_detect.bus.I2CBusProtocol` implementation:

.. code-block:: python

   from stemma_detect import scan_all

   report = scan_all(existing_bus)

Reports can be serialized directly with :meth:`~stemma_detect.scanner.ScanReport.to_dict` or
:meth:`~stemma_detect.scanner.ScanReport.to_json`. These classes and functions are re-exported from
the top-level ``stemma_detect`` package as shown above.

Confirming expected hardware
----------------------------

Applications can explicitly confirm possible matches while creating an installation plan. Include
the mux path in the expectation key so identically addressed devices on different channels remain
distinct:

.. code-block:: python

   from stemma_detect import create_install_plan, install_drivers

   expected = {((), 0x48): "pcf8591"}

   def confirm_possible(sensor):
       return expected.get((sensor.path, sensor.address)) == sensor.name

   plan = create_install_plan(report, confirm_possible=confirm_possible)
   results = install_drivers(plan)

Definitive detections are always included. Unconfirmed possible detections are omitted, conflicting
confirmations at one physical location are rejected, and packages are deduplicated.

Bus
---

.. automodule:: stemma_detect.bus
   :members:

Catalog
-------

.. automodule:: stemma_detect.catalog
   :members:

Results
-------

.. automodule:: stemma_detect.result
   :members:

Scanner
-------

.. automodule:: stemma_detect.scanner
   :members:

Serialization
-------------

.. automodule:: stemma_detect.serialization
   :members:

Installation
------------

.. automodule:: stemma_detect.installer
   :members:
