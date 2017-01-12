import os
import unittest
from abc import ABCMeta

from hgicommon.testing import create_tests, TestUsingType, TypeUsedInTest
from useintest.predefined.irods.models import Version
from useintest.predefined.samtools import samtools_executable_controllers
from useintest.tests.executables.common import run

EXAMPLE_BAM = os.path.join(os.path.dirname(os.path.realpath(__file__)), "example.bam")
assert os.path.exists(EXAMPLE_BAM)


class _TestSamtoolsExecutablesController(TestUsingType[TypeUsedInTest], metaclass=ABCMeta):
    """
    Tests for executables controllers for Samtools.
    """

    def setUp(self):
        self.controller = self.get_type_to_test()()
        self.version = Version(self.get_type_to_test().__name__.replace("Samtools", "")
                               .replace("ExecutablesController", "").replace("_", "."))
        self.executables_location = self.controller.write_executables()
        self.samtools_location = os.path.join(self.executables_location, "samtools")

    def tearDown(self):
        self.controller.tear_down()

    def test_help(self):
        out, _ = run([self.samtools_location, "--help"])
        self.assertIn("Version: %s" % self.version, out)

    def test_view(self):
        original_sam_contents, _ = run([self.samtools_location, "view", "-O", "SAM", EXAMPLE_BAM], decode_output_to=None)
        sam_contents, _ = run([self.samtools_location, "view", "-O", "SAM", EXAMPLE_BAM], decode_output_to=None)
        self.assertEqual(original_sam_contents, sam_contents)


# Setup tests
globals().update(create_tests(_TestSamtoolsExecutablesController, samtools_executable_controllers))

# Fix for stupidity of test runners
del _TestSamtoolsExecutablesController, TestUsingType, create_tests

if __name__ == "__main__":
    unittest.main()
