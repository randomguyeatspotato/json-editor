import gi
from gi.repository import Gtk

class EntryFieldBoolean(Gtk.ComboBox):
    def __init__(self, convert):
        Gtk.ComboBox.__init__(self)

        model = Gtk.ListStore(str)
        model.append([convert(False)])
        model.append([convert(True)])

        renderer = Gtk.CellRendererText()

        self.set_model(model)
        self.pack_start(renderer, True)
        self.add_attribute(renderer, "text", 0)
        self.set_entry_text_column(0)
        self.set_active(0)

    def get_value(self):
        return [False, True][self.get_active()]
