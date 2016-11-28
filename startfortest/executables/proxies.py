import atexit
import logging
import os
import shutil
import tempfile
from typing import Dict, Set, Optional

from docker.errors import NotFound

from hgicommon.docker.client import create_client
from hgicommon.helpers import create_random_string
from startfortest._common import reduce_whitespace
from startfortest.executables.builders import CommandsBuilder
from startfortest.executables.common import CLI_ARGUMENTS
from startfortest.executables.models import Executable

_SHEBANG = "#!/usr/bin/env bash"
_FAIL_SETTINGS = "set -eu -o pipefail"


class ExecutablesController:
    """
    Controller for proxy executables that execute commands in a transparent Docker container.
    """
    @staticmethod
    def _write_commands(location: str, commands: str):
        """
        Writes the commands to a file at the given location. Will overwrite any pre-existing file.
        :param location: the location to write the commands to
        :param commands: the commands to write
        """
        with open(location, "w") as file:
            file.write("%s\n" % _SHEBANG)
            file.write("%s\n" % _FAIL_SETTINGS)
            file.write(commands)
        os.chmod(location, 0o700)

    def __init__(self, image_with_real_binaries: str, run_container_command_builder: Optional[CommandsBuilder]=None):
        """
        Constructor.
        :param image_with_real_binaries: the name (docker-py's "tag") of the Docker image that the proxied binaries are
        executed within
        :param run_container_command_builder: (optional) builder for commands used to start up persistent container in
        which comamnds should be run (can lead to much better performance because new container is not brought up each
        time)
        """
        self.docker_image_with_binaries = image_with_real_binaries
        self.run_container_command_builder = run_container_command_builder

        self._cached_container_name = create_random_string(prefix="execution-container-")
        self.run_container_command_builder.name = self._cached_container_name
        self.run_container_command_builder.detached = True

        # Ensure the image with the real binaries have been pulled to stop it polluting the output
        if ":" in image_with_real_binaries:
            repository, tag = image_with_real_binaries.split(":")
        else:
            repository, tag = image_with_real_binaries, None
        docker_client = create_client()
        docker_image = docker_client.images("%s:%s" % (repository, tag), quiet=True)
        if len(docker_image) == 0:
            for line in docker_client.pull(image_with_real_binaries, stream=True):
                logging.debug(line)

        atexit.register(self.tear_down)

    def tear_down(self):
        """
        Tears down the controller.
        """
        docker_client = create_client()
        try:
            docker_client.remove_container(self._cached_container_name, force=True)
        except NotFound:
            """ Not concerned if the container had not yet been created """

    def create_executable_commands(self, executable: Executable) -> str:
        """
        Creates executable commands for the given executable.
        :param executable: the executable to create comamnds for
        :return: the created commands
        """
        if executable.uses_running_container:
            if self.run_container_command_builder is None:
                raise ValueError("No command to run execution container defined.")
            executable.commands_builder.container = self._cached_container_name

            return reduce_whitespace("""
                isRunning() {
                    [ $(docker ps -f name=%(uuid)s | wc -l | awk '{print $1}') -eq 2 ]
                }

                if ! isRunning;
                then
                    startIfNotRunning() {
                        if ! isRunning
                        then
                            %(container_setup)s > /dev/null
                        fi
                    }
                    lock=".%(uuid)s.lock"
                    if type flock > /dev/null 2>&1
                    then
                        # Linux
                        (
                            flock 10
                            startIfNotRunning
                            rm -f /tmp/${lock}
                        ) 10> /tmp/${lock}
                    elif type lockfile > /dev/null 2>&1
                    then
                        # Mac
                        lockfile /tmp/${lock}
                        startIfNotRunning
                        rm -f /tmp/${lock}
                    else
                        # No supported lock functionality - blindly try to start it and ignore any error
                        set +e
                        startIfNotRunning 2> /dev/null
                        set -e
                    fi
                fi

                %(to_execute)s
            """ % {
                "uuid": self._cached_container_name,
                "container_setup": self.run_container_command_builder.build().rstrip(),
                "to_execute": executable.commands_builder.build()
            })
        else:
            return executable.commands_builder.build()

    def create_simple_executable_commands(self, containerised_executable: str, executable_arguments=CLI_ARGUMENTS) -> str:
        """
        TODO
        :param containerised_executable:
        :param executable_arguments:
        :return:
        """
        containerised_executable = containerised_executable.replace('"', '\\"')
        to_execute = CommandsBuilder(executable=containerised_executable, container=self._cached_container_name,
                                     executable_arguments=[executable_arguments])
        return self.create_executable_commands(Executable(to_execute, True))


class DefinedExecutablesController(ExecutablesController):
    """
    TODO
    """
    def __init__(self, *args, named_executables: Dict[str, Executable], **kwargs):
        super().__init__(*args, **kwargs)
        self._temp_directories = set()  # type: Set[str]
        self.named_executables = named_executables

    def tear_down(self):
        """
        TOOD
        :return:
        """
        super().tear_down()
        while len(self._temp_directories) > 0:
            directory = self._temp_directories.pop()
            shutil.rmtree(directory, ignore_errors=True)

    def write_executables(self, location: str=None) -> str:
        """
        Writes the defined executables to the given location. If no location is given, they shall be written to a
        temporary directory.
        :param location: (optional) location to write the executables to
        :return: the directory containing the executables
        """
        if location is None:
            location = tempfile.mkdtemp(prefix="executables-", dir="/tmp")
            self._temp_directories.add(location)

        for name, executable in self.named_executables.items():
            executable_location = os.path.join(location, name)
            commands = self.create_executable_commands(executable)
            ExecutablesController._write_commands(executable_location, commands)

        return location
