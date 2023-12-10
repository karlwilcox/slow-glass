# standard libraries
# local modules
import commands


class Dispatcher:

    def __init__(self):
        self.command_list = []
        for command in commands.Command.__subclasses__():
            self.command_list.append(command())

    def dispatch(self, action, scene):
        if not action.complete:
            if self.find_command(action.expanded_line, scene):
                action.complete = True

    def find_command(self, content, scene):
        complete = None
        for command in self.command_list:
            if command.invoked(content):
                complete = command.process(scene)
                break
        if complete is None:
            print("Unknown command: %s" % content)
            return True
        return complete

    def print_help(self):
        for command in self.command_list:
            print(command.help)
