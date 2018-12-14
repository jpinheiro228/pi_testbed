import os
import subprocess

DHCP_LEASES = "/var/lib/misc/dnsmasq.leases"
PI = {0: {"mac": "",
          "hostname": ""},
      1: {"mac": "b8:27:eb:bf:6e:49",
          "hostname": ""}}


def get_pi_ip(pi=None):
    leases = []

    if pi:
        with open(DHCP_LEASES, "r") as f:
            for l in f.readlines():
                if PI[pi]["mac"] in l:
                    leases.append(l.split(" ")[2])
    return leases


def add_pi_user(pi, username):
    pi_ip = get_pi_ip(pi)[0]
    ssh_command = "ssh root@{} -i /home/jpinheiro/.ssh/vms \"bash create_user.sh {}\"".format(pi_ip, username)
    code = subprocess.call(ssh_command, shell=True)
    error = None
    if code != 0:
        error = "Something went wrong."
    print(ssh_command)
    return code, error


def allocate_pi(pi):
    pi_ip = get_pi_ip(pi)[0]
    ssh_command = "ssh root@{} -i /home/jpinheiro/.ssh/vms \"who | wc -l\"".format(pi_ip, username)
    code = subprocess.call(ssh_command, shell=True)


def upload_to_pi():
    pass


if __name__ == '__main__':
    get_pi_ip()
    add_pi_user(1, "ezequias")
