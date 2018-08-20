#!/bin/bash

# Installing dependencies 

sudo apt-get -y install git cmake g++ python-dev swig \
pkg-config libfftw3-dev libboost-all-dev libcppunit-dev libgsl-dev \
libusb-dev libsdl1.2-dev python-wxgtk3.0 python-numpy python-cheetah \
python-lxml doxygen libxi-dev python-sip libqt4-opengl-dev libqwt-dev \
libfontconfig1-dev libxrender-dev python-sip python-sip-dev python-qt4 \
python-sphinx libusb-1.0-0-dev libcomedi-dev libzmq3-dev python-mako

# GNURadio + RTL-SDR

sudo apt install gnuradio

sudo apt install rtl-sdr gr-osmosdr

