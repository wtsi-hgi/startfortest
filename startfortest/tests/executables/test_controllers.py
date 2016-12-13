import os
import shutil
import subprocess
import tempfile
import unittest
from typing import Set, List, Tuple

from hgicommon.helpers import create_random_string
from startfortest.executables.builders import CommandsBuilder, MountedArgumentParser
from startfortest.executables.common import write_commands
from startfortest.executables.controllers import ExecutablesController
from startfortest.executables.models import Executable
from startfortest.tests.executables._common import MOUNTABLE_TEMP_DIRECTORY, MAX_RUN_TIME_IN_SECONDS, \
    get_builder_for_commands_to_run_persistent_ubuntu, UBUNTU_IMAGE_TO_TEST_WITH

_CONTENT = "Hello World!"
_CAT_MOUNTED_ARGUMENT_PARSER = MountedArgumentParser(
    positional_arguments=MountedArgumentParser.ALL_POSITIONAL_ARGUMENTS).build()
_TOUCH_MOUNTED_ARGUMENT_PARSER = MountedArgumentParser(
    named_arguments={"-r"}, positional_arguments=MountedArgumentParser.ALL_POSITIONAL_ARGUMENTS).build()


class TestExecutablesController(unittest.TestCase):
    """
    Tests for ExecutablesController.
    """
    def setUp(self):
        self._temp_files = set()    # type: Set[str]
        self.controller = ExecutablesController()
        self.persistent_run_controller = ExecutablesController(get_builder_for_commands_to_run_persistent_ubuntu())

    def tearDown(self):
        self.controller.tear_down()
        self.persistent_run_controller.tear_down()
        while len(self._temp_files) > 0:
            directory = self._temp_files.pop()
            shutil.rmtree(directory, ignore_errors=True)

    def test_create_executable_commands_with_no_running_container(self):
        commands_builder = CommandsBuilder("echo", image=UBUNTU_IMAGE_TO_TEST_WITH, executable_arguments=[_CONTENT])
        commands = self.controller.create_executable_commands(Executable(commands_builder, False))
        out, error = self._run_commands(commands)
        self.assertEqual(_CONTENT, out)

    def test_create_executable_commands_with_positional_parameter_needing_mounting_for_read(self):
        read_file = self._create_mountable_temp_file()
        with open(read_file, "w") as file:
            file.write(_CONTENT)

        commands_builder = CommandsBuilder(
            "cat", image=UBUNTU_IMAGE_TO_TEST_WITH, get_path_arguments_to_mount=_CAT_MOUNTED_ARGUMENT_PARSER)
        commands = self.controller.create_executable_commands(Executable(commands_builder, False))
        out, error = self._run_commands(commands, [read_file])
        self.assertEqual(_CONTENT, out)

    def test_create_executable_commands_with_positional_parameter_needing_mounting_for_write(self):
        with tempfile.TemporaryDirectory(dir=MOUNTABLE_TEMP_DIRECTORY) as temp_directory:
            file_locations = [os.path.join(temp_directory, create_random_string()) for _ in range(5)]
            commands_builder = CommandsBuilder(
                "touch", image=UBUNTU_IMAGE_TO_TEST_WITH, get_path_arguments_to_mount=_TOUCH_MOUNTED_ARGUMENT_PARSER)
            commands = self.controller.create_executable_commands(Executable(commands_builder, False))
            self._run_commands(commands, file_locations)

            for location in file_locations:
                self.assertTrue(os.path.exists(location))

    def test_create_executable_commands_with_named_parameters_needing_mounting(self):
        with tempfile.TemporaryDirectory(dir=MOUNTABLE_TEMP_DIRECTORY) as temp_directory:
            commands_builder = CommandsBuilder(
                "touch", image=UBUNTU_IMAGE_TO_TEST_WITH, get_path_arguments_to_mount=_TOUCH_MOUNTED_ARGUMENT_PARSER,
                mounts={temp_directory: temp_directory})
            commands = self.persistent_run_controller.create_executable_commands(Executable(commands_builder, False))

            test_file = os.path.join(temp_directory, "test-file")
            reference = self._create_mountable_temp_file()
            os.utime(reference, (0, 0))
            self._run_commands(commands, ["-r", reference, test_file])
            self.assertEqual(0.0, os.path.getmtime(test_file))

    def test_create_simple_executable_commands_that_raises_exception(self):
        commands = self.persistent_run_controller.create_simple_executable_commands("cat", "/does-not-exist")
        out, error = self._run_commands(commands, raise_if_stderr=False)
        self.assertNotEqual("", error)
        self.assertEqual("", out)

    def test_create_simple_executable_commands_execute_in_same_container(self):
        test_file_location = "/test-file"
        self._run_commands(self.persistent_run_controller.create_simple_executable_commands("touch", test_file_location))
        out, error = self._run_commands(self.persistent_run_controller.create_simple_executable_commands("ls", test_file_location))
        self.assertEqual(test_file_location, out)

    def test_create_simple_executable_commands_without_parameters(self):
        commands = self.persistent_run_controller.create_simple_executable_commands("cat", "/etc/lsb-release")
        out, error = self._run_commands(commands)
        key_values = {line.split("=")[0]: line.split("=")[1] for line in out.split("\n")}
        self.assertEqual("Ubuntu", key_values["DISTRIB_ID"])

    def test_create_simple_executable_commands_with_parameters(self):
        commands = self.persistent_run_controller.create_simple_executable_commands("echo")
        out, error = self._run_commands(commands, [_CONTENT])
        self.assertEqual(out, _CONTENT)

    def _run_commands(self, commands: str, arguments: List=None, raise_if_stderr: bool=True) -> Tuple[str, str]:
        """
        Saves the given commands as an executable and runs it with the given arguments.
        :param commands: the commands to execute
        :param arguments: the arguments to be passed to the executable
        :param raise_if_stderr: whether the test should raise an exception if anything is written to standard error
        :return: tuple where the first element is what was written to standard out and the second is what was written to
        standard error
        """
        if arguments is None:
            arguments = []

        location = self._create_mountable_temp_file()
        write_commands(location, commands)
        arguments.insert(0, location)

        process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = process.communicate(timeout=MAX_RUN_TIME_IN_SECONDS)
        out = out.decode("utf-8").rstrip("\n")
        error = error.decode("utf-8")

        if raise_if_stderr and len(error) > 0:
            raise ValueError("Unexpected output on standard error:\n%s" % error)

        return out, error

    def _create_mountable_temp_file(self) -> str:
        """
        Creates a temp file with only a lifespan of the test, which can be mounted.
        :return: the location of the temp file
        """
        _, location = tempfile.mkstemp(dir=MOUNTABLE_TEMP_DIRECTORY, text=True)
        self._temp_files.add(location)
        return location


if __name__ == "__main__":
    unittest.main()
