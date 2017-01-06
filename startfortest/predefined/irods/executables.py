import os
import subprocess
from typing import Sequence

from startfortest.executables.builders import CommandsBuilder, MountedArgumentParserBuilder
from startfortest.executables.controllers import DefinedExecutablesController
from startfortest.executables.models import Executable


class IrodsExecutablesController(DefinedExecutablesController):
    """
    TODO
    """
    _ICOMMAND_EXECUTABLES = {"ibun", "icd", "ichksum", "ichmod", "icp", "idbug", "ienv", "ierror", "iexecmd", "iexit",
                             "ifsck", "iget", "igetwild", "ihelp", "iinit", "ilocate", "ils", "ilsresc", "imcoll",
                             "imiscsvrinfo", "imkdir", "imv", "ipasswd", "iphybun", "iphymv", "ips", "iput", "ipwd",
                             "iqdel", "iqmod", "iqstat", "iquest", "iquota", "ireg", "irepl", "irm", "irmtrash",
                             "irsync", "irule", "iscan", "isysmeta", "itrim", "iuserinfo", "ixmsg", "izonereport",
                             "imeta", "iadmin"}
    _GET_POSITIONAL_ARGUMENTS_TO_MOUNT = MountedArgumentParserBuilder(
        positional_arguments=MountedArgumentParserBuilder.ALL_POSITIONAL_ARGUMENTS).build()
    _DEFAULT_SETTINGS_DIRECTORIES = {"/root/.irods", "/home/root/.irods"}

    def __init__(self, irods_container_name: str, image_with_compatible_icommands: str, settings_directory_on_host: str,
                 settings_directories_in_container: Sequence[str]=_DEFAULT_SETTINGS_DIRECTORIES):
        """
        Constructor.
        :param irods_container_name:
        :param image_with_compatible_icommands:
        :param settings_directory_on_host:
        :param settings_directories_in_container:
        """
        self._image_with_compatible_icommands = image_with_compatible_icommands
        self._run_container_commands_builder = CommandsBuilder(
            "sleep", executable_arguments=["infinity"], image=image_with_compatible_icommands,
            other_docker="--link %s" % irods_container_name,
            mounts={settings_directory_on_host: set(settings_directories_in_container)})
        super().__init__(run_container_commands_builder=self._run_container_commands_builder)
        self._register_named_executables()

    def authenticate(self, executables_directory: str, password: str):
        """
        TODO
        :param executables_directory:
        :param password:
        :return:
        """
        process = subprocess.Popen([os.path.join(executables_directory, "iinit"), password], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, error = process.communicate()
        if len(error) > 0:
            raise Exception("Error authenticating to iCAT server with password \"%s\": %s" % (password, error))

    def write_executables_and_authenticate(self, password: str, location: str=None) -> str:
        """
        TODO
        :param password:
        :param location:
        :return:
        """
        location = self.write_executables(location)
        self.authenticate(location, password)
        return location

    def _register_named_executables(self):
        """
        TODO
        :return:
        """
        for icommand in IrodsExecutablesController._ICOMMAND_EXECUTABLES - {"iget", "iput"}:
            self.named_executables[icommand] = Executable(CommandsBuilder(icommand), True)

        def create_executable_template(command: str):
            commands_builder = CommandsBuilder(
                command, image=self._image_with_compatible_icommands,
                get_path_arguments_to_mount=IrodsExecutablesController._GET_POSITIONAL_ARGUMENTS_TO_MOUNT,
                mounts=self._run_container_commands_builder.mounts,
                other_docker=self._run_container_commands_builder.other_docker)
            return Executable(commands_builder, False)

        # Note: if `-` is the second positional argument with `iget`, `-` is suspected as a file, relative to the
        # current directory. This leads to an unnecessary mount and the use of `-w` to change the working directory.
        self.named_executables["iget"] = create_executable_template("iget")
        self.named_executables["iput"] = create_executable_template("iput")
