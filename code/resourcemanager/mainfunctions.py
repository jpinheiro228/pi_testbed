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
        """

        :param dom_name:
        :param num_cpu:
        :param mem:
        :return:
        """
        with open("xmlExample.xml", "r") as f:
            default_xml = f.read()

        default_xml = default_xml.replace("{NAME}", dom_name)
        default_xml = default_xml.replace("{CPU}", str(num_cpu))
        default_xml = default_xml.replace("{MEMORY}", str(mem))

        domain = self.conn.defineXML(default_xml)
        return domain

    def start_domain(self, dom_name=None, domain=None):
        """

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
        """

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

    def delete_domain(self, dom_name=None):
        raise NotImplementedError("This function was not implemented.")

    def clone_domain(self, src_dom_name=None, dst_dom_name=None):
        raise NotImplementedError("This function was not implemented.")


if __name__ == '__main__':
    # This main function is for testing purposes only.
    # Will be removed once all functions are tested.
    c = VirtInstance()
    # c.create_domain("tst")
    # c.start_domain("tst")
    c.stop_domain("tst")
    c.conn.close()
