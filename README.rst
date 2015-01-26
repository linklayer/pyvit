======
CANard
======

CANard is a library for dealing with Controller Area Network (CAN) data from
Python.

Using a CANtact
===============

The [CANtact](http://cantact.io) tool is directly supported by CANard. Using it
requires pySerial, which can be installed with `pip install pyserial`.

Example
-------

This examples goes on bus and prints received messages::
    from canard import can
    from canard.hw import cantact

    dev = cantact.CantactDev("/dev/cu.usbmodem14511")

    dev.start()
    while True:
	print(dev.recv())

You will need to set the serial port (/dev/cu.usbmodem14511 in this example)
correctly.


Using Peak CAN Tools
====================

Peak CAN tools (also known as GridConnect) are support through SocketCAN. This
functionality is only available on Linux

For kernels 3.6 and newer, skip to step 5.

1. Download the [Linux
driver](http://www.peak-system.com/fileadmin/media/linux/index.htm#download)

2. Install dependancies
    `sudo apt-get install libpopt-dev`

3. Build the driver:
    `cd peak-linux-driver-x.xx`
    `make`
    `sudo make install`

4. Enable the driver
    `sudo modprobe pcan`

5. Connect a Peak CAN tool, ensure it appears in `/proc/pcan`

6. Set the bitrate
