import logging
import os
import unittest
from abc import ABCMeta, abstractmethod

from testwithirods.irods_3_controller import Irods3_3_1ServerController
from testwithirods.irods_4_controller import Irods4_1_8ServerController, Irods4_1_9ServerController

# TODO: The reliance here on baton is not great
icat_setups = {
    Irods3_3_1ServerController: "mercury/baton:0.16.4-with-irods-3.3.1",
    Irods4_1_8ServerController: "mercury/baton:0.16.4-with-irods-4.1.8",
    Irods4_1_9ServerController: "mercury/baton:0.16.4-with-irods-4.1.9"
}


class IcatTest(unittest.TestCase, metaclass=ABCMeta):
    """
    Base class in which tests on iCAT servers should extend if they wish to test all iCAT setups.
    """
    @property
    @abstractmethod
    def ServerController(self) -> type:
        """
        The server controller for the iCAT server being tested
        :return: the server controller
        """

    @property
    @abstractmethod
    def compatible_baton_image(self) -> str:
        """
        A baton image that is compatible to run queries against the iCAT server being tested.
        :return: the docker baton image name
        """


def _create_test_for_baton_setup(controller_type: type, compatible_baton_image: str, test_superclass: type):
    """
    Creates tests for single baton setup.
    :param controller_type: the controller for the version of iCAT being tested
    :param compatible_baton_image: version of baton compatible with the version of iRODS that is controlled
    :param test_superclass: the test superclass
    """
    class_name = "%s%s" % (controller_type.__name__, test_superclass.__name__)
    globals()[class_name] = type(
        class_name,
        (test_superclass,),
        {
            "ServerController": property(lambda self: controller_type),
            "compatible_baton_image": property(lambda self: compatible_baton_image)
        }
    )


def create_tests_for_all_irods_setups(test_superclass: type):
    """
    Creates tests for all icat setups, where tests should be made to inherit from the given test superclass.
    :param test_superclass: test superclass, which must inherit from `IcatTest`
    """
    single_setup = os.environ.get("SINGLE_TEST_SETUP")
    if single_setup:
        controller_type = globals()[single_setup]
        compatible_baton_image = icat_setups[controller_type]
        _create_test_for_baton_setup(controller_type, compatible_baton_image, test_superclass)
    else:
        for controller_type, compatible_baton_image in icat_setups.items():
            _create_test_for_baton_setup(controller_type, compatible_baton_image, test_superclass)


# Turn on logging by default to better get to the bottom of Travis CI timeout issues
logging.root.setLevel(logging.DEBUG)