from startfortest.executables.builders import CommandsBuilder

MOUNTABLE_TEMP_DIRECTORY = "/tmp"
MAX_RUN_TIME_IN_SECONDS = 120
UBUNTU_IMAGE_TO_TEST_WITH = "ubuntu:16.04"


def get_builder_for_commands_to_run_persistent_ubuntu() -> CommandsBuilder:
    """
    TODO
    :return:
    """
    return CommandsBuilder("sleep", image=UBUNTU_IMAGE_TO_TEST_WITH, executable_arguments=["infinity"])
