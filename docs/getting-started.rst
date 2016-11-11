===============
Getting Started
===============

Using a CANtact
===============

The CANtact_ tool is directly supported by pyvit. It should work on Windows,
OS X, and Linux.

.. _CANtact: http://cantact.io/

Example
-------

This examples goes on bus and prints received messages:

.. code:: python

    from pyvit import can
    from pyvit.hw.cantact import CantactDev

    dev = CantactDev("/dev/cu.usbmodem1451")
    dev.set_bitrate(500000)
    dev.start()
    while True:
	  print(dev.recv())

You will need to set the serial port (``/dev/cu.usbmodem1451`` in this example)
correctly.

SocketCAN
=========

SocketCAN interfaces are supported, however they are only available on Linux.
Using SocketCAN requires Python 3+

Example
-------

The device can now be accessed as a ``SocketCanDev``. This examples goes on bus
and prints received messages:

.. code:: python

    from pyvit import can
    from pyvit.hw import socketcan

    dev = socketcan.SocketCanDev("can0")

    dev.start()
    while True:
	print(dev.recv())

.. _`Linux driver`: http://www.peak-system.com/fileadmin/media/linux/index.htm#download

Using Peak CAN Tools
====================

Peak CAN tools (also known as GridConnect) are support through SocketCAN. This
functionality is only available on Linux

For kernels 3.6 and newer, skip to step 5.

1. Download the Peak `Linux driver`_.

2. Install dependancies::

    sudo apt-get install libpopt-dev

3. Build the driver::

    cd peak-linux-driver-x.xx
    make
    sudo make install

4. Enable the driver::

    sudo modprobe pcan

5. Connect a Peak CAN tool, ensure it appears in ``/proc/pcan``. Note the
   network device name (ie, ``can0``)

6. Bring the corresponding network up::

     sudo ifconfig can0 up
