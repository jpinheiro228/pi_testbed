#!/usr/bin/env bash

rm /home/ubuntu/.bash_history

rm /etc/machine-id

/bin/systemd-machine-id-setup

mv /etc/rc.local /etc/rc.local.bkp

/bin/rm -v /etc/ssh/ssh_host_*

dpkg-reconfigure openssh-server

/sbin/reboot