from startfortest.executables.builders import CommandsBuilder, MountedArgumentParser
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
    _GET_POSITIONAL_ARGUMENTS_TO_MOUNT = MountedArgumentParser(
        positional_arguments=MountedArgumentParser.ALL_POSITIONAL_ARGUMENTS).build()

    def __init__(self, irods_container_name: str, image_with_compatible_icommands: str,
                 settings_directory_on_host: str, settings_directory_in_container: str="/root/.irods"):
        self._image_with_compatible_icommands = image_with_compatible_icommands
        self._run_container_commands_builder = CommandsBuilder(
            "sleep", executable_arguments=["infinity"], image=image_with_compatible_icommands,
            other_docker="--link %s" % irods_container_name,
            mounts={settings_directory_on_host: settings_directory_in_container})
        super().__init__(run_container_commands_builder=self._run_container_commands_builder)
        self._register_named_executables()

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

        self.named_executables["iget"] = create_executable_template("iget")
        self.named_executables["iput"] = create_executable_template("iput")
