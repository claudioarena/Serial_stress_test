# UART Serial Stress Test

Simple python script to stress test a UART device (such as a USB to serial port device).
For this to work, you need to short out the Rx and Tx lines together.

The script works by sending out random strings using the serial port, and then verifying that the received string matches the one we transmitted.

The script verifies this for many serial Baud Rates, and for strings of varying lengths. It also checks multiple times for each length (i.e. it regenerate different random strings).

Note that this only test valid Unicode strings. It should however be a good test that the device is working.
