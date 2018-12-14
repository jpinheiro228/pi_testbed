### Digital Modulation

In this example, QPSK symbols are transmitted and the I&Q samples are saved
in a dat file on the receiver. This samples are processed offline, using
the digital_rx_demod.grc file.

The digital_rx.grc file to be runned at the receiver (Raspberry PI + RTL-SDR)
  capture and save the I&Q samples.

The Mpsk_TX.grc file to be runned at the transmitter (VM + USRP) sends the QPSK
 symbols.
