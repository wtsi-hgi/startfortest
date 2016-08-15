import unittest
from abc import ABCMeta

import testwithirods
from hgicommon.docker.client import create_client
from testwithirods.helpers import SetupHelper
from testwithirods.irods_contoller import IrodsServerController
from testwithirods.models import ContainerisedIrodsServer
from testwithirods.proxies import ICommandProxyController
from testwithirods.tests._common import create_tests_for_all_icat_setups, IcatTest


class TestIrodsServerController(IcatTest, metaclass=ABCMeta):
    """
    Tests for `IrodsServerController`.
    """
    @staticmethod
    def _is_container_running(container: ContainerisedIrodsServer) -> bool:
        """
        Gets whether the given container is running. Will raise an exception if the container does not exist.
        :param container: the container
        :return: whether the container is running
        """
        docker_client = create_client()
        return docker_client.inspect_container(container.native_object)["State"]["Running"]

    def setUp(self):
        self.irods_controller = self.ServerController()     # type: IrodsServerController

    def test_start_server(self):
        irods_server = self.irods_controller.start_server()
        self.assertTrue(type(self)._is_container_running(irods_server))
        self.assertIn(irods_server, self.irods_controller.running_containers)

        repository, tag = self.compatible_baton_image.split(":")
        create_client().pull(repository, tag)

        proxy_controller = ICommandProxyController(irods_server, self.compatible_baton_image)
        icommand_binaries_location = proxy_controller.create_proxy_binaries()
        setup_helper = SetupHelper(icommand_binaries_location)

        self.assertEqual(setup_helper.get_icat_version(), irods_server.version)

    def test_stop_server(self):
        irods_server = self.irods_controller.start_server()
        assert type(self)._is_container_running(irods_server)
        assert irods_server in self.irods_controller.running_containers
        self.irods_controller.stop_server(irods_server)
        self.assertFalse(type(self)._is_container_running(irods_server))
        self.assertNotIn(irods_server, self.irods_controller.running_containers)

    def test_tear_down(self):
        irods_servers = [self.irods_controller.start_server() for _ in range(3)]
        self.irods_controller.tear_down()
        for irods_server in irods_servers:
            self.assertFalse(type(self)._is_container_running(irods_server))


# Setup tests for all iCAT setups
create_tests_for_all_icat_setups(TestIrodsServerController)
for name, value in testwithirods.tests._common.__dict__.items():
    if TestIrodsServerController.__name__ in name:
        globals()[name] = value
del TestIrodsServerController


if __name__ == "__main__":
    unittest.main()
