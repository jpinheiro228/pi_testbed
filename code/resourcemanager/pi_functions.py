import tarfile
import os

PI_FS_ROOT = "/home/jpinheiro/client/"
DEFAULT_FS = "/home/jpinheiro/client.tar"


def extract_fs(c_name="client"):
    fs_file = tarfile.open(DEFAULT_FS)

    if not os.path.isdir(PI_FS_ROOT + c_name):
        os.mkdir(PI_FS_ROOT + c_name)

    fs_file.extractall(path=PI_FS_ROOT + c_name)

    fs_file.close()


def customize_pi(c_name):
    hosts = "127.0.0.1   localhost\n"\
            "::1         localhost ip6-localhost ip6-loopback\n"\
            "ff02::1     ip6-allnodes\n"\
            "ff02::2     ip6-allrouters\n"\
            "127.0.1.1   " + c_name

    with open(PI_FS_ROOT + c_name + "/etc/hostname", "w") as f:
        f.write(c_name)

    with open(PI_FS_ROOT + c_name + "/etc/hosts", "w") as f:
        f.write(hosts)


def turn_on_pi(c_name):
    with open("/tftp-pi/cmdline.txt", "w") as f:
        f.write("root=/dev/nfs nfsroot=10.0.0.1:/nfs/{},vers=3 "
                "rw ip=dhcp rootwait elevator=deadline".format(c_name))
    # Relay code here!


if __name__ == '__main__':
    extract_fs("test")
    customize_pi("test")
