#!/bin/bash


mkdir gnuradio git
cd git
git clone https://github.com/gnuradio/pybombs.git
cd pybombs
sudo python setup.py install

pybombs recipes add gr-recipes git+https://github.com/gnuradio/gr-recipes.git  
pybombs recipes add gr-etcetera git+https://github.com/gnuradio/gr-etcetera.git

pybombs prefix init ~/gnuradio

sudo pybombs install gnuradio

sudo pybombs install rtl-sdr gr-osmosdr

sudo ldconfig 

sudo source ~/gnuradio/setup_env.sh

# test
# gnuradio-companion


