#!/bin/bash

if [ $USER != "root" ]; then
    echo "Please run this script as root!"
    exit 1
fi

sudo add-apt-repository ppa:ettusresearch/uhd

sudo apt update

#install Xorg
sudo apt-get -y install xorg openbox

# Install gnuradio
sudo apt-get -y install git cmake g++ python-dev swig libvolk1-dev \
pkg-config libfftw3-dev libboost-all-dev libcppunit-dev libgsl-dev \
libusb-dev libsdl1.2-dev python-wxgtk3.0 python-numpy python-cheetah \
python-lxml doxygen libxi-dev python-sip libqt4-opengl-dev libqwt-dev \
libfontconfig1-dev libxrender-dev python-sip python-sip-dev python-qt4 \
python-sphinx libusb-1.0-0-dev libcomedi-dev libzmq3-dev python-mako \
python-gtk2-dev libuhd-dev uhd-host libvolk1-bin libuhd003.010.003

sudo uhd_images_downloader

volk_profile

git clone --recursive http://gnuradio.org/git/gnuradio.git

cd gnuradio
git checkout v3.7.13.4
mkdir build
cd build
cmake ../
make -j4
sudo make install

export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/dist-packages
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

sudo ldconfig

sudo addgroup usrp
sudo usermod -aG usrp ubuntu
echo 'ACTION=="add", BUS=="usb", SYSFS{idVendor}=="fffe", 
SYSFS{idProduct}=="0002", GROUP:="usrp", MODE:="0660"' > tmpfile
sudo chown root.root tmpfile
sudo mv tmpfile /etc/udev/rules.d/10-usrp.rules

sudo /etc/init.d/udev stop
sudo /etc/init.d/udev start
