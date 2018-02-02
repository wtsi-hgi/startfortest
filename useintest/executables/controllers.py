import atexit
import os
from copy import deepcopy

from docker.errors import NotFound
from temphelpers import TempManager
from typing import Dict, Optional, Type
from uuid import uuid4

from useintest.common import MOUNTABLE_TEMP_DIRECTORY, docker_client
from useintest.executables.builders import CommandsBuilder
from useintest.executables.common import CLI_ARGUMENTS, write_commands, pull_docker_image
from useintest.executables.models import Executable

_TAB_AS_SPACES = "    "


def _reduce_whitespace(string: str) -> str:
    """
    Reduces the whitespace in the given command.
    :param string: the command to reduce whitespace from
    :return: command with reduced whitespace
    """
    leading_tabs = int(min({(len(line) - len(line.lstrip(_TAB_AS_SPACES))) / len(_TAB_AS_SPACES)
                            for line in string.split("\n") if len(line.strip()) > 0}))
    stripped = []
    for line in string.split("\n"):
        stripped.append(line.replace(_TAB_AS_SPACES, "", leading_tabs))
    return "\n".join(stripped)


class ExecutablesController:
    """
    Controller for proxy executables that execute commands in a transparent Docker container.
    """
    def __init__(self, run_container_commands_builder: Optional[CommandsBuilder]=None):
        """
        Constructor.
        :param image_with_real_binaries: the name (docker-py's "tag") of the Docker image that the proxied binaries are
        executed within
        :param run_container_commands_builder: (optional) builder for commands used to start up persistent container in
        which commands should be run (can lead to much better performance because new container is not brought up each
        time)
        """
        self.run_container_command_builder = run_container_commands_builder

        if run_container_commands_builder is not None:
            if run_container_commands_builder.image is None:
                raise ValueError("Run container command builder must define the image the container is to use")
            pull_docker_image(run_container_commands_builder.image)
            self._cached_container_name = f"execution-container-{uuid4()}"
            self.run_container_command_builder.name = self._cached_container_name
            self.run_container_command_builder.detached = True

        atexit.register(self.tear_down)

    def tear_down(self):
        """
        Tears down the controller.
        """
        if self.run_container_command_builder is not None:
            try:
                container = docker_client.containers.get(self._cached_container_name)
                container.stop()
                container.remove(force=True)
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

            return _reduce_whitespace("""
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
            pull_docker_image(executable.commands_builder.image)
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
    def __init__(self, run_container_commands_builder: Optional[CommandsBuilder]=None,
                 named_executables: Dict[str, Executable]=None):
        super().__init__(run_container_commands_builder)
        self._temp_manager = TempManager()
        self.named_executables = named_executables if named_executables is not None else dict()

    def tear_down(self):
        """
        TOOD
        :return:
        """
        super().tear_down()
        self._temp_manager.tear_down()

    def write_executables(self, location: str=None) -> str:
        """
        Writes the defined executables to the given location. If no location is given, they shall be written to a
        temporary directory.
        :param location: (optional) location to write the executables to
        :return: the directory containing the executables
        """
        if location is None:
            location = self._temp_manager.create_temp_directory(prefix="executables-", dir=MOUNTABLE_TEMP_DIRECTORY)

        for name, executable in self.named_executables.items():
            executable_location = os.path.join(location, name)
            commands = self.create_executable_commands(executable)
            write_commands(executable_location, commands)

        return location


class DefinedExecutablesControllerTypeBuilder:
    """
    TODO
    """
    def __init__(self, type_name: str, named_executables: Dict[str, Executable]):
        """
        TODO
        :param type_name:
        :param named_executables:
        """
        self.type_name = type_name
        self.named_executables = named_executables

    def build(self) -> Type[DefinedExecutablesController]:
        """
        TODO
        :return:
        """
        named_executables = deepcopy(self.named_executables)

        def init(controller: DefinedExecutablesController, *args, **kwargs):
            super(type(controller), controller).__init__(*args, named_executables=named_executables, **kwargs)

        return type(
            self.type_name,
            (DefinedExecutablesController, ),
            {"__init__": init}
        )
