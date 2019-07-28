#!/bin/bash

pacman -S qemu libvirt ebtables dnsmasq bridge-utils virt-manager openbsd-netcat

usermod -aG libvirt $USER

echo '

#################################################################
#
# Network connectivity controls
#
listen_tls = 0
listen_tcp = 1
listen_addr = "0.0.0.0"

#################################################################
#
# UNIX socket access controls
#
unix_sock_group = "libvirt"
unix_sock_ro_perms = "0777"
unix_sock_rw_perms = "0770"

#################################################################
#
# Authentication.
#
auth_unix_ro = "none"
auth_unix_rw = "none"
' >> /etc/libvirt/libvirtd.conf
