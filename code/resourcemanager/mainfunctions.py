import libvirt
import os
import xmltodict
import json
import xml.etree.ElementTree as ET

LIBVIRT_URI = "qemu:///system"

dom_state = {0: "No State",
             1: "Running",
             2: "Blocked",
             3: "Paused",
             4: "Shutdown",
             5: "Shut off",
             6: "Crashed",
             7: "PM Suspended"}

with open('usrps.txt', 'r') as f:
    usrplist = f.read().replace("'''", '"""').split(",")[0:-1]

num = 0
usrp_dict = {}
for i in usrplist:
    usrp_dict[num] = i
    num += 1
print("{} USRPs where detected.".format(len(usrp_dict)))

ag = libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT


class VirtInstance:
    def __init__(self, uri=LIBVIRT_URI):
        try:
            self.conn = self.connect(uri)
        except Exception as e:
            print(e)
            exit(1)
        self.uri = uri
        self.domains = {}
        self.update_dom_dict()
        self.default_pool = self.get_default_spool()

    @staticmethod
    def connect(uri=LIBVIRT_URI):
        """Opens a connection to LIBVIRT

        The default URI is "qemu:///system"

        :param uri: Hypervisor URI
        :return: virConnect object
        """
        conn = libvirt.open(uri)
        if conn is None:
            raise Exception("Could not open connection to the HYPERVISOR")
        return conn

    def get_default_spool(self):
        """Gets the default storage pool.

        :return:
        """
        default_pool = self.conn.storagePoolLookupByName('default')
        return default_pool

    def update_dom_dict(self):
        """ Returns a dictionary of domains of the Hypervisor

        The dictionary will be in the format NAME:ID

        :return: Dictionary of Names and IDs for the domains
        """
        all_domains = self.conn.listAllDomains()
        dom_dict = {}
        for dom in all_domains:
            if dom.name() != "default":
                state, maxmem, mem, cpus, cput = dom.info()
                dom_dict[dom.name()] = {"id": dom.ID(),
                                        "name": dom.name(),
                                        "status": dom_state[state],
                                        "cpus": cpus,
                                        "memory": mem / 2 ** 10,
                                        "ip": "",
                                        "usrp": self.has_usrp(dom.name())}
                if dom.isActive():
                    try:
                        dom_dict[dom.name()]["ip"] = dom.interfaceAddresses(ag, 0)['ens3']["addrs"][0]["addr"]
                    except Exception as e:
                        dom_dict[dom.name()]["ip"] = "Not available"
        self.domains = dom_dict

    def create_domain(self, dom_name=None, num_cpu=1, mem=1):
        """Create a domain using the default XML and a default disk.

        :param dom_name:
        :param num_cpu:
        :param mem:
        :return:
        """
        with open(os.path.dirname(os.path.abspath(__file__)) + "/domain_xmlExample.xml", "r") as f:
            default_xml = f.read()

        default_xml = default_xml.replace("{NAME}", dom_name)
        default_xml = default_xml.replace("{CPU}", str(num_cpu))
        default_xml = default_xml.replace("{MEMORY}", str(mem))

        try:
            self.clone_disk("default", dom_name)
            domain = self.conn.defineXML(default_xml)
        except Exception as e:
            raise e

        return domain

    def start_domain(self, dom_name=None, domain=None):
        """Start a domain.

        :param dom_name:
        :param domain:
        :return:
        """
        if (not domain) and (dom_name is not None):
            domain = self.conn.lookupByName(dom_name)

        if domain.create() < 0:
            raise Exception("The domain cold not be started.")
        return domain

    def stop_domain(self, dom_name=None, force_in_error=True, domain=None):
        """stops a domain.

        :param dom_name:
        :param force_in_error:
        :param domain:
        :return:
        """
        if (not domain) and (dom_name is not None):
            domain = self.conn.lookupByName(dom_name)

        if (domain.shutdown() < 0) and (force_in_error is True):
            domain.destroy()
            return 1
        return 0

    def delete_domain(self, dom_name=None, domain=None):
        """Completely remove a domain and its disks.

        :param dom_name:
        :param domain:
        :return:
        """
        if dom_name is not None:
            domain = self.conn.lookupByName(dom_name)
        elif not domain:
            raise Exception("A domain object or domain name must be provided.")

        domain_disk = self.default_pool.storageVolLookupByName(domain.name()
                                                               + ".qcow2")
        if domain.isActive():
            domain.destroy()
        domain.undefine()
        domain_disk.wipe(0)
        domain_disk.delete(0)

        return 0

    def clone_domain(self, src_dom_name=None, dst_dom_name=None):
        raise NotImplementedError("This function was not implemented.")

    def list_disks(self):
        """Returns a list of disks in the Default Storage Pool.

        :return:
        """
        return self.default_pool.listVolumes()

    def clone_disk(self, src_dom_name=None, dst_dom_name=None):
        """Clone a volume.

        :param src_dom_name:
        :param dst_dom_name:
        :return:
        """
        disk_list = self.list_disks()

        if dst_dom_name + ".qcow2" in disk_list:
            raise Exception("Destination disk {} already exists.".format(dst_dom_name))
        elif src_dom_name + ".qcow2" not in disk_list:
            raise Exception("Source disk {} does not exist.".format(src_dom_name))

        src_vol = self.default_pool.storageVolLookupByName(src_dom_name + ".qcow2")
        src_info = src_vol.info()

        with open(os.path.dirname(os.path.abspath(__file__)) + "/disk_xmlExample.xml", "r") as f:
            default_xml = f.read()
        default_xml = default_xml.replace("{NAME}", dst_dom_name)
        default_xml = default_xml.replace("{SIZE}", str(src_info[1]))
        default_xml = default_xml.replace("{ALLOCATION}", str(src_info[2]))

        if not self.default_pool.createXMLFrom(default_xml, src_vol, 0):
            raise Exception("Something went wrong with the volume clonning.")
        return 0

    def attach_usrp(self, dom_name, usrp_num=0):
        domain = self.conn.lookupByName(dom_name)
        dom_xml = domain.XMLDesc()

        root = ET.fromstring(dom_xml)
        devices = root.find("devices")
        usrp = devices.find("hostdev")
        if usrp:
            raise Exception("This VM already has an USRP")
        else:
            devices.append(ET.fromstring(usrp_dict[usrp_num]))
            domain.undefine()
            self.conn.defineXML(ET.tostring(root).decode())
        return "Success"

    def detach_usrp(self, dom_name):
        domain = self.conn.lookupByName(dom_name)
        dom_xml = domain.XMLDesc()
        root = ET.fromstring(dom_xml)
        devices = root.find("devices")
        usrp = devices.find("hostdev")
        if usrp:
            devices.remove(usrp)
            domain.undefine()
            self.conn.defineXML(ET.tostring(root).decode())
        return "Success"

    def has_usrp(self, dom_name):
        domain = self.conn.lookupByName(dom_name)
        dom_xml = domain.XMLDesc()
        root = ET.fromstring(dom_xml)
        devices = root.find("devices")
        usrp = devices.find("hostdev")
        if usrp:
            return True
        else:
            return False

    def n_usrp(self):
        return len(usrp_dict)


if __name__ == '__main__':
    # This main function is for testing purposes only.
    # Will be removed once all functions are tested.
    try:
        c = VirtInstance()
        # c.create_domain("USRP2")
        c.detach_usrp("USRP")
        # c.attach_usrp("USRP",0)
        # c.start_domain("test")
        # input("RET to continue...")
        # c.stop_domain("test", True)
        # input("RET to continue...")
        # c.start_domain("test")
        # input("RET to continue...")
        # c.delete_domain("test")
        c.conn.close()
    except Exception as e:
        print(e)
