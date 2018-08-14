import libvirt

LIBVIRT_URI = "qemu:///system"


class VirtInstance:
    def __init__(self, uri=LIBVIRT_URI):
        try:
            self.conn = self.connect(uri)
        except Exception as e:
            print(e)

    def connect(self, uri=LIBVIRT_URI):
        """Opens a connection to LIBVIRT

        :param uri: Hypervisor URI
        :return: virConnect object
        """
        conn = libvirt.open(uri)
        if conn is None:
            raise Exception("Could not open connection to LIBVIRT HYPERVISOR")
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


if __name__ == '__main__':
    c = VirtInstance()
    print(c.list_domains())
    c.conn.close()