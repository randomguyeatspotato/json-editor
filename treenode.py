import json
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject

class TreeNode(GObject.GObject):
    def __init__(self, key, value):
        GObject.GObject.__init__(self)
        self.key = key
        self.value = value

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value

    def get_string(self):
        string = ""
        if type(self.key) == str:
            string += '"' + self.key + '": '

        string += json.dumps(self.value)

        return string

GObject.type_register(TreeNode)
