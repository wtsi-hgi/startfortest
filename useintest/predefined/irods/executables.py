import shutil
import subprocess
from abc import ABCMeta

from typing import Sequence, Type

from useintest.executables.builders import CommandsBuilder, MountedArgumentParserBuilder
from useintest.executables.controllers import DefinedExecutablesController
from useintest.executables.models import Executable
from useintest.models import Version


class IrodsAuthenticatiableExecutablesController(DefinedExecutablesController, metaclass=ABCMeta):
    """
    Defined executable controller that can authenticate its common executables container against iRODS.
    """
    def authenticate(self, password: str):
        """
        Authenticates the common container against the iCAT server.
        :param password: password associated with the settings that are being used in the common container
        """
        # Assumes all baton containers have icommands installed
        name = "iinit"
        executable = Executable(CommandsBuilder(name), True)
        directory = self._temp_manager.create_temp_directory()
        location = self._write_executable(directory, name, executable)

        process = subprocess.Popen([location, password], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = process.communicate()
        if len(error) > 0:
            raise Exception("Error authenticating to iCAT server with password \"%s\": %s" % (password, error))

        shutil.rmtree(directory)

    def write_executables_and_authenticate(self, password: str, location: str=None) -> str:
        """
        Both writes the executables to the given location and then authenticates to use the server with the given
        password.
        :param password: password used by the `authenticate` method
        :param location: location used by the `write_executables` method
        :return: the location of the written executables
        """
        location = self.write_executables(location)
        self.authenticate(password)
        return location


class IrodsBaseExecutablesController(IrodsAuthenticatiableExecutablesController, metaclass=ABCMeta):
    """
    Executables (icomands) for use against an iRODS server (iCAT).
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

    # TODO: Could add option to connect to iRODS server not running in Docker (i.e. via port opposed to link)
    def __init__(self, irods_container_name: str, image_with_compatible_icommands: str, settings_directory_on_host: str,
                 settings_directories_in_container: Sequence[str]=_DEFAULT_SETTINGS_DIRECTORIES):
        """
        Constructor.
        :param irods_container_name: the name of the container running the iRODS server
        :param image_with_compatible_icommands: image containing icommands that are compatible with the iRODS server
        :param settings_directory_on_host: directory on the Docker host machine that are used to access iRODS
        :param settings_directories_in_container: the directories on the container running the Docker image that need to
        contain the settings
        """
        self._image_with_compatible_icommands = image_with_compatible_icommands
        run_container_commands_builder = CommandsBuilder(
            "sleep", executable_arguments=["infinity"], image=image_with_compatible_icommands,
            other_docker="--link %s" % irods_container_name,
            mounts={settings_directory_on_host: set(settings_directories_in_container)})
        super().__init__(run_container_commands_builder=run_container_commands_builder)
        self._register_named_executables()

    def _register_named_executables(self):
        """
        Registers the executables that can be written by this controller.
        """
        for icommand in IrodsBaseExecutablesController._ICOMMAND_EXECUTABLES - {"iget", "iput"}:
            self.named_executables[icommand] = Executable(CommandsBuilder(icommand), True)

        def create_executable_template(command: str):
            commands_builder = CommandsBuilder(
                command, image=self._image_with_compatible_icommands,
                get_path_arguments_to_mount=IrodsBaseExecutablesController._GET_POSITIONAL_ARGUMENTS_TO_MOUNT,
                mounts=self.run_container_commands_builder.mounts,
                other_docker=self.run_container_commands_builder.other_docker)
            return Executable(commands_builder, False)

        # Note: if `-` is the second positional argument with `iget`, `-` is suspected as a file, relative to the
        # current directory. This leads to an unnecessary mount and the use of `-w` to change the working directory.
        self.named_executables["iget"] = create_executable_template("iget")
        self.named_executables["iput"] = create_executable_template("iput")


def _build_irods_executables_controller_type(image_with_compatible_icommands: str, irods_version: Version) \
        -> Type[IrodsBaseExecutablesController]:
    """
    Builds an iRODS executables controller for the given icommands image.
    :param image_with_compatible_icommands: image with icommands
    :param irods_version: version of iRODS icommands are for
    :return: built controller type
    """
    def init(self, *args, **kwargs):
        args = list(args)
        args.insert(1, image_with_compatible_icommands)
        args = tuple(args)
        super(type(self), self).__init__(*args, **kwargs)

    return type(
        "Irods%sExecutablesController" % str(irods_version).replace(".", "_"),
        (IrodsBaseExecutablesController,),
        {"__init__": init}
    )


Irods3_3_1ExecutablesController = _build_irods_executables_controller_type("mercury/icat:3.3.1", Version("3.3.1"))
Irods4_1_8ExecutablesController = _build_irods_executables_controller_type("mercury/icat:4.1.8", Version("4.1.8"))
Irods4_1_9ExecutablesController = _build_irods_executables_controller_type("mercury/icat:4.1.9", Version("4.1.9"))
Irods4_1_10ExecutablesController = _build_irods_executables_controller_type("mercury/icat:4.1.10", Version("4.1.10"))
IrodsExecutablesController = Irods4_1_10ExecutablesController

irods_executables_controllers_and_versions = {
    Version("3.3.1"): Irods3_3_1ExecutablesController,
    Version("4.1.8"): Irods4_1_8ExecutablesController,
    Version("4.1.9"): Irods4_1_9ExecutablesController,
    Version("4.1.10"): Irods4_1_10ExecutablesController,
}
irods_executables_controllers = list(irods_executables_controllers_and_versions.values())
