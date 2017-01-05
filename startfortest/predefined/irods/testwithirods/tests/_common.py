import logging
import os
import unittest
from abc import ABCMeta, abstractmethod
from typing import Set, Type

from startfortest.predefined.irods.testwithirods.irods_4_controller import Irods4_1_8ServerController, Irods4_1_9ServerController, \
    Irods4_1_10ServerController
from testwithirods.irods_3_controller import Irods3_3_1ServerController
from testwithirods.irods_contoller import IrodsServerController
from testwithirods.models import IrodsServer

icat_controllers = {Irods3_3_1ServerController, Irods4_1_8ServerController,
                    Irods4_1_9ServerController, Irods4_1_10ServerController}


def get_image_with_compatible_icat_binaries(irods_server: IrodsServer) -> str:
    """
    TODO
    :param irods_server:
    :return:
    """
    return "mercury/icat:%s" % irods_server.version


class IcatTest(unittest.TestCase, metaclass=ABCMeta):
    """
    Base class in which tests on iCAT servers should extend if they wish to test all iCAT setups.
    """
    @property
    @abstractmethod
    def ServerController(self) -> Type[IrodsServerController]:
        """
        The server controller for the iCAT server being tested
        :return: the server controller
        """


def create_tests_for_all_irods_setups(test_superclass: Type[IcatTest]):
    """
    Creates tests for all icat setups, where tests should be made to inherit from the given test superclass.
    :param test_superclass: test superclass, which must inherit from `IcatTest`
    """
    controller_types = set()   # type: Set[Type[IrodsServerController]]
    single_setup = os.environ.get("SINGLE_TEST_SETUP")
    if single_setup:
        controller_types.add(globals()[single_setup])
    else:
        controller_types = controller_types.union(icat_controllers)

    for controller_type in controller_types:
        class_name = "%s%s" % (controller_type.__name__, test_superclass.__name__)
        globals()[class_name] = type(
            class_name,
            (test_superclass,),
            {"ServerController": property(lambda self: controller_type)}
        )


# Turn on logging by default
logging.root.setLevel(logging.DEBUG)
