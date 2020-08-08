import gi
from gi.repository import Gtk

class EntryFieldDictionary(Gtk.Label):
    def __init__(self, convert):
        Gtk.Label.__init__(self)

        self.set_text(convert({}))

    def set_value(self, value):
        pass

    def get_value(self):
        return {}
