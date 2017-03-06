from abc import abstractproperty, ABCMeta

from typing import Set, Any, List, Type

from useintest.executables.builders import CommandsBuilder
from useintest.executables.models import Executable
from useintest.predefined.irods.executables import IrodsAuthenticatedExecutablesController
from useintest.predefined.irods.models import Version


class BatonBaseExecutablesController(IrodsAuthenticatedExecutablesController, metaclass=ABCMeta):
    """
    Executables (icomands) for use against an iRODS server (iCAT).
    """
    _BATON_BINARIES = {"baton", "baton-metaquery", "baton-get", "baton-chmod", "baton-list", "baton-metamod",
                       "baton-specificquery", "iinit"}

    @staticmethod
    @abstractproperty
    def baton_version() -> Version:
        """
        Gets the version of baton used.
        :return: the baton version
        """

    @staticmethod
    @abstractproperty
    def irods_version() -> Version:
        """
        Gets the version of iRODS that baton has been compiled to work with.
        :return: the compatible version of iRODS
        """

    # TODO: Must be able to work via a port or container!
    def __init__(self, baton_image: str, irods_container_name: str, irods_settings_directory: str):
        # """
        # Constructor.
        # :param irods_container_name: the name of the container running the iRODS server
        # :param image_with_compatible_icommands: image containing icommands that are compatible with the iRODS server
        # :param settings_directory_on_host: directory on the Docker host machine that are used to access iRODS
        # :param settings_directories_in_container: the directories on the container running the Docker image that need
        # to contain the settings
        # """
        self._run_container_commands_builder = CommandsBuilder(
            "sleep", executable_arguments=["infinity"], image=baton_image,
            other_docker="--link %s" % irods_container_name,
            mounts={irods_settings_directory: "/root/.irods"})
        super().__init__(run_container_commands_builder=self._run_container_commands_builder)
        self._register_named_executables()

    def _register_named_executables(self):
        """
        Registers the executables that can be written by this controller.
        """
        save_mounts = {"baton-get"}

        for baton_executable in BatonBaseExecutablesController._BATON_BINARIES - save_mounts:
            self.named_executables[baton_executable] = Executable(CommandsBuilder(baton_executable), True)

        def _get_save_mounts(cli_arguments: List[Any]) -> Set[str]:
            if "--save" in cli_arguments:
                raise ValueError("--save is not currently supported (redirect to a file instead)")
            return set()

        for baton_executable in save_mounts:
            self.named_executables[baton_executable] = Executable(
                CommandsBuilder(baton_executable, get_path_arguments_to_mount=_get_save_mounts), True)


def _build_baton_executables_controller(baton_image: str, irods_version: Version, baton_version: Version) \
        -> Type[BatonBaseExecutablesController]:
    """
    TODO
    :param baton_image:
    :param irods_version:
    :param baton_version:
    :return:
    """
    def init(self, *args, **kwargs):
        super(type(self), self).__init__(baton_image, *args, **kwargs)

    return type(
        "Baton%sExecutablesController" % str(irods_version).replace(".", "_"),
        (BatonBaseExecutablesController,),
        {
            "__init__": init,
            "irods_version": lambda: irods_version,
            "baton_version": lambda: baton_version
        }
    )


Baton0_17_0WithIrods4_1_10ExecutablesController = _build_baton_executables_controller(
    "mercury/baton:0.17.0-with-irods-4.1.10", Version("4.1.10"), Version("0.17.0"))
BatonExecutablesController = Baton0_17_0WithIrods4_1_10ExecutablesController

baton_executables_controllers = {Baton0_17_0WithIrods4_1_10ExecutablesController}
