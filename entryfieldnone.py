import gi
from gi.repository import Gtk

class EntryFieldNone(Gtk.Label):
    def __init__(self, convert):
        Gtk.Label.__init__(self)

        self.set_text(convert(None))

    def get_value(self):
        return None
