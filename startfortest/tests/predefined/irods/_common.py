import os
from typing import Type, Set

from startfortest.predefined.irods.services import IrodsServiceController, irods_service_controllers
from startfortest.tests.service.common import TestServiceControllerSubclass


def create_tests_for_all_irods_setups(test_superclass: Type[TestServiceControllerSubclass]):
    """
    Creates tests for all icat setups, where tests should be made to inherit from the given test superclass.
    :param test_superclass: test superclass, which must inherit from `IcatTest`
    """
    controller_types = set()   # type: Set[Type[IrodsServiceController]]
    single_setup = os.environ.get("SINGLE_TEST_SETUP")
    if single_setup:
        controller_types.add(globals()[single_setup])
    else:
        controller_types = controller_types.union(irods_service_controllers)

    for controller_type in controller_types:
        class_name = "%s%s" % (controller_type.__name__, test_superclass.__name__)
        globals()[class_name] = type(
            class_name,
            (test_superclass,),
            {"_get_controller_type": staticmethod((lambda controller_type: lambda: controller_type)(controller_type))}
        )
