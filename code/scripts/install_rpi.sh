#!/bin/bash

# Updating the package list and installing dependencies

echo
echo Updating package list...
echo

sudo apt-get update

sudo apt-get install libcanberra-gtk-module

# Listed dependencies:
#sudo apt-get -y install git cmake g++ python-dev swig \
#kg-config libfftw3-dev libboost-all-dev libcppunit-dev libgsl-dev \
#libusb-dev libsdl1.2-dev python-wxgtk3.0 python-numpy python-cheetah \
#python-lxml doxygen libxi-dev python-sip libqt4-opengl-dev libqwt-dev \
#libfontconfig1-dev libxrender-dev python-sip python-sip-dev python-qt4 \
#python-sphinx libusb-1.0-0-dev libcomedi-dev libzmq3-dev python-mako

# Installing GNURadio + RTL-SDR 

echo
echo Installing GNURadio and RTL-SDR...
echo

sudo apt install gnuradio rtl-sdr gr-osmosdr

echo
echo Done.
echo
