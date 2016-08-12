import unittest

from icat.api import IrodsVersion
from icat.api import get_static_irods_server_controller
from icat.models import Version


class TestGetStaticIrodsServerController(unittest.TestCase):
    """
    Tests for `get_static_irods_server_controller`.
    """
    def test_get_v_3_3_1(self):
        StaticIrodsController = get_static_irods_server_controller(IrodsVersion.v3_3_1)
        irods_server = StaticIrodsController.start_server()
        self.assertEqual(irods_server.version, Version("3.3.1"))
        StaticIrodsController.stop_server(irods_server)

    def test_get_v_4_1_8(self):
        StaticIrodsController = get_static_irods_server_controller(IrodsVersion.v4_1_8)
        irods_server = StaticIrodsController.start_server()
        self.assertEqual(irods_server.version, Version("4.1.8"))
        StaticIrodsController.stop_server(irods_server)

    def test_get_v_4_1_9(self):
        StaticIrodsController = get_static_irods_server_controller(IrodsVersion.v4_1_9)
        irods_server = StaticIrodsController.start_server()
        self.assertEqual(irods_server.version, Version("4.1.9"))
        StaticIrodsController.stop_server(irods_server)


if __name__ == "__main__":
    unittest.main()
