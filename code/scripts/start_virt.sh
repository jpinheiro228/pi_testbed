#!/bin/bash

systemctl start libvirtd.service
systemctl start virtlogd.service
virsh net-start default
