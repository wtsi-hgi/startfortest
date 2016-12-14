import os
import unittest
from abc import ABCMeta
from typing import Type

from startfortest.executables.controllers import DefinedExecutablesController
from startfortest.executables.predefined.samtools import Samtools1_3_1_ExecutablesController
from startfortest.tests.executables._common import run

EXAMPLE_BAM = os.path.join(os.path.dirname(os.path.realpath(__file__)), "example.bam")
assert os.path.exists(EXAMPLE_BAM)

CONTROLLERS = {
    Samtools1_3_1_ExecutablesController: "1.3.1"
}


class _TestSamtoolsExecutablesController(unittest.TestCase, metaclass=ABCMeta):
    """
    Tests for executables controllers for Samtools.
    """
    def __init__(self, controller_type: Type[DefinedExecutablesController], version: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._controller_type = controller_type
        self._version = version

    def setUp(self):
        self.controller = Samtools1_3_1_ExecutablesController()
        self.executables_location = self.controller.write_executables()
        self.samtools_location = os.path.join(self.executables_location, "samtools")

    def tearDown(self):
        self.controller.tear_down()

    def test_help(self):
        out, _ = run([self.samtools_location, "--help"])
        self.assertIn("Version: %s" % self._version, out)

    def test_view(self):
        original_sam_contents, _ = run([self.samtools_location, "view", "-O", "SAM", EXAMPLE_BAM], decode_output_to=None)
        sam_contents, _ = run([self.samtools_location, "view", "-O", "SAM", EXAMPLE_BAM], decode_output_to=None)
        self.assertEqual(original_sam_contents, sam_contents)


for controller, version in CONTROLLERS.items():
    name = "Test%s" % controller.__name__

    def init(controller: _TestSamtoolsExecutablesController, *args, **kwargs):
        super(type(controller), controller).__init__(controller, version, *args, **kwargs)

    globals()[name] = type(
        name,
        (_TestSamtoolsExecutablesController,),
        {"__init__": init}
    )


# Hack for unittest
del _TestSamtoolsExecutablesController


if __name__ == "__main__":
    unittest.main()
