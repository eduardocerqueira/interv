"""
Codes on this file are only for demonstration purpose and might not be 
executable.

:topic Pyhton in general
:level basic

"""

from logging import getLogger
from time import sleep
from uuid import uuid4

from os import getenv
from os.path import join, exists
from re import search, IGNORECASE
from glanceclient.v2.client import Client as gclient
from keystoneclient.v2_0.client import Client as kclient
from novaclient.client import Client as nclient
from novaclient.exceptions import ClientException, NotFound
from novaclient.v2 import networks, images, flavors

LOG = getLogger(__name__)


class Nova(object):
    """Class to group interactions with Openstack nova client or api.
    http://docs.openstack.org/developer/python-novaclient/
    """

    def __init__(self, user_credential):
        self.version = "2"
        self.user_cred = user_credential
        self.nova = nclient(
            self.version,
            username=self.user_cred['OS_USERNAME'],
            password=self.user_cred['OS_PASSWORD'],
            auth_url=self.user_cred['OS_AUTH_URL'],
            project_name=self.user_cred['OS_PROJECT_NAME']
        )
        self.neutron = networks.NeutronManager(self.nova)
        self.images = images.GlanceManager(self.nova)
        self.flavors = flavors.FlavorManager(self.nova)

    @retry(NovaPasswordError, tries=20)
    def get_password(self, server_name, keypair):
        """Return the password for a server using the private key.

        :param server_name: Name of the server to check password
        :type server_name: str
        :param keypair: SSH private key
        :type keypair: str
        :return: Admin password
        :rtype: str
        """
        try:
            server = self.get_server(server_name)
            password = server.get_password(keypair)

            if not password:
                raise NovaPasswordError("Password is empty!")
            if not isinstance(password, str):
                raise NovaPasswordError("Password: %s is not a string type!" %
                                        password)
            LOG.debug("Admin password for %s is %s", server_name, password)
        except NovaPasswordError as ex:
            raise NovaPasswordError(ex.msg)

        return password

    def get_server(self, instance_name):
        """Get nova server and return all info"""
        try:
            return self.nova.servers.find(name=instance_name)
        except Exception:
            return None

    def delete_instance(self, instance_id):
        """Delete a server."""
        self.nova.servers.delete(instance_id)

    def flavor_exist(self, flavor):
        """Verify flavor exists in tenant.

        :param flavor: Size of vm to create.
        """
        LOG.debug('Checking openstack flavor %s' % flavor)
        try:
            self.flavors.find(id=flavor)
        except ClientException:
            LOG.error("Flavor: %s size does not exist!", flavor)
            raise ClientException(1)

    def image_exist(self, image_name):
        """Check to see if image exists in tenant.

        :param image_name: name of image declared in resources.yaml
        """
        LOG.debug('Checking openstack image %s' % image_name)
        try:
            self.images.find_image(image_name)
        except ClientException:
            LOG.error("Image: %s does not exist!", image_name)
            raise ClientException(1)

    def network_exist(self, network):
        """Verify network exists in tenant.

        :param network: Network to create vms on.
        """
        LOG.debug('Checking openstack network %s' % network)
        try:
            self.neutron.find_network(network)
        except ClientException:
            LOG.error("Network: %s does not exist!", network)
            raise ClientException(1)

    def keypair_exist(self, keypair):
        """Verify key pair exists in tenant.

        :param keypair: SSH keypair.
        """
        LOG.debug('Checking openstack keypair %s' % keypair)
        try:
            self.nova.keypairs.find(name=keypair)
        except ClientException:
            LOG.error("Keypair: %s does not exist!", keypair)
            raise ClientException(1)