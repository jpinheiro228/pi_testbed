#!/bin/bash

systemctl start libvirtd.service
systemctl start virtlogd.service

sleep 1

virsh net-start default
