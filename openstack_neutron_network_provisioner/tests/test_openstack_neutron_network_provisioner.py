import logging
import random
import string
import unittest

import openstack_neutron_network_provisioner.tasks as tasks

RANDOM_LEN = 3  # cosmo_test_neutron_XXX_something

class OpenstackNetworkProvisionerTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("test_openstack_host_provisioner")
        self.logger.level = logging.DEBUG
        self.logger.info("setUp called")
        self.neutron_client = tasks._init_client()
        self.name_prefix = 'cosmo_test_neutron_{0}_'.format(''.join(
            [random.choice(string.ascii_uppercase + string.digits) for i in range(RANDOM_LEN)]
        ))

    def tearDown(self):
        # CLI all tests cleanup:
        # neutron net-list | awk '/cosmo_test_/ {print $2}' | xargs -n1 neutron net-delete
        for net in self.neutron_client.list_networks()['networks']:
            if net['name'].startswith(self.name_prefix):
                self.neutron_client.delete_network(net['id'])

    def test_all(self):
        name = self.name_prefix + 'net1'
        network = {'name': name}

        tasks.provision(network)
        network = tasks._get_network_by_name(self.neutron_client, name)
        self.assertIsNotNone(network)
        self.assertTrue(network['admin_state_up'])

        tasks.stop(network)
        network = tasks._get_network_by_name(self.neutron_client, name)
        self.assertFalse(network['admin_state_up'])

        tasks.start(network)
        network = tasks._get_network_by_name(self.neutron_client, name)
        self.assertTrue(network['admin_state_up'])

        tasks.terminate(network)
        network = tasks._get_network_by_name(self.neutron_client, name)
        self.assertIsNone(network)


if __name__ == '__main__':
    unittest.main()
