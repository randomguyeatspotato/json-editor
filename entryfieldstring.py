import gi
from gi.repository import Gtk

class EntryFieldString(Gtk.Entry):

    def __init__(self, convert):
        Gtk.Entry.__init__(self)

        self.set_placeholder_text(convert(str))

    def set_value(self, value):
        self.set_text(value)

    def get_value(self):
        return self.get_text()
