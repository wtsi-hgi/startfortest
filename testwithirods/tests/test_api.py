import unittest

from testwithirods.api import IrodsVersion
from testwithirods.api import get_static_irods_server_controller
from testwithirods.models import Version


class TestGetStaticIrodsServerController(unittest.TestCase):
    """
    Tests for `get_static_irods_server_controller`.
    """
    def test_get_v_3_3_1(self):
        StaticIrodsController = get_static_irods_server_controller(IrodsVersion.v3_3_1)
        try:
            irods_server = StaticIrodsController.start_server()
            self.assertEqual(irods_server.version, Version("3.3.1"))
        finally:
            StaticIrodsController.tear_down()

    def test_get_v_4_1_8(self):
        StaticIrodsController = get_static_irods_server_controller(IrodsVersion.v4_1_8)
        try:
            irods_server = StaticIrodsController.start_server()
            self.assertEqual(irods_server.version, Version("4.1.8"))
        finally:
            StaticIrodsController.tear_down()

    def test_get_v_4_1_9(self):
        StaticIrodsController = get_static_irods_server_controller(IrodsVersion.v4_1_9)
        try:
            irods_server = StaticIrodsController.start_server()
            self.assertEqual(irods_server.version, Version("4.1.9"))
        finally:
            StaticIrodsController.tear_down()

    def test_get_v_4_1_10(self):
        StaticIrodsController = get_static_irods_server_controller(IrodsVersion.v4_1_10)
        try:
            irods_server = StaticIrodsController.start_server()
            self.assertEqual(irods_server.version, Version("4.1.10"))
        finally:
            StaticIrodsController.tear_down()


if __name__ == "__main__":
    unittest.main()
