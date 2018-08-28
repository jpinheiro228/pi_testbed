import libvirt

LIBVIRT_URI = "qemu:///system"


class VirtInstance:
    def __init__(self, uri=LIBVIRT_URI):
        try:
            self.conn = self.connect(uri)
        except Exception as e:
            print(e)
            exit(1)
        self.uri = uri
        self.domains = self.get_dom_dict()
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

    def get_dom_dict(self):
        """ Returns a dictionary of domains of the Hypervisor

        The dictionary will be in the format NAME:ID

        :return: Dictionary of Names and IDs for the domains
        """
        all_domains = self.conn.listAllDomains()
        dom_dict = {}
        for dom in all_domains:
            dom_dict[dom.name()] = dom.ID()
        return dom_dict

    def create_domain(self, dom_name=None, num_cpu=1, mem=1):
        """Create a domain using the default XML and a default disk.

        :param dom_name:
        :param num_cpu:
        :param mem:
        :return:
        """
        with open("domain_xmlExample.xml", "r") as f:
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

    def stop_domain(self, dom_name=None, force_in_error=False, domain=None):
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
            if domain.shutdown() < 0:
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

        if dst_dom_name+".qcow2" in disk_list:
            raise Exception("Destination disk {} already exists.".format(dst_dom_name))
        elif src_dom_name+".qcow2" not in disk_list:
            raise Exception("Source disk {} does not exist.".format(src_dom_name))

        src_vol = self.default_pool.storageVolLookupByName(src_dom_name+".qcow2")
        src_info = src_vol.info()

        with open("disk_xmlExample.xml", "r") as f:
            default_xml = f.read()
        default_xml = default_xml.replace("{NAME}", dst_dom_name)
        default_xml = default_xml.replace("{SIZE}", str(src_info[1]))
        default_xml = default_xml.replace("{ALLOCATION}", str(src_info[2]))

        if not self.default_pool.createXMLFrom(default_xml, src_vol, 0):
            raise Exception("Something went wrong with the volume clonning.")
        return 0


if __name__ == '__main__':
    # This main function is for testing purposes only.
    # Will be removed once all functions are tested.
    try:
        c = VirtInstance()
        c.delete_domain("test")
        c.conn.close()
    except Exception as e:
        print(e)
