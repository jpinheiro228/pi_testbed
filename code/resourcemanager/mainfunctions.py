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

    def list_domains(self):
        """ Returns a dictionary in the format NAME:ID of all domains of the HYPERVISOR

        :return: Dictionary of Names and IDs for the domains
        """
        allDomains = self.conn.listAllDomains()
        domDict = {}
        for dom in allDomains:
            domDict[dom.name()] = dom.ID()
        return domDict

    def create_domain(self):
        raise NotImplementedError("This function was not implemented.")

    def start_domain(self, dom_name=None):
        raise NotImplementedError("This function was not implemented.")

    def stop_domain(self, dom_name=None):
        raise NotImplementedError("This function was not implemented.")

    def destroy_domain(self, dom_name=None):
        raise NotImplementedError("This function was not implemented.")

    def clone_domain(self, src_dom_name=None, dst_dom_name=None):
        raise NotImplementedError("This function was not implemented.")


if __name__ == '__main__':
    # This main function is for testing purposes only.
    # Will be removed once all functions are tested.
    c = VirtInstance()
    print(c.list_domains())
    print(c.start_domain())
    c.conn.close()
