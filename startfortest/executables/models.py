from hgicommon.models import Model
from startfortest.executables.builders import CommandsBuilder


class Executable(Model):
    """
    Model of an executable.
    """
    def __init__(self, commands_builder: CommandsBuilder, uses_running_container: bool=True):
        self.commands_builder = commands_builder
        self.uses_running_container = uses_running_container

