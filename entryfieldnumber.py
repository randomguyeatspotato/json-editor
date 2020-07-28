import re
import gi
from gi.repository import Gtk

class EntryFieldNumber(Gtk.Entry):

    def __init__(self, convert):
        Gtk.Entry.__init__(self)

        print(convert(float))
        self.set_placeholder_text(convert(float))

        def on_insert(entry, text, length, position):
            new_string = entry.get_text()
            p = entry.props.cursor_position
            new_string = new_string[:p] + text + new_string[p:]
            pattern = r'-?\d*(\d[.]\d*)?([eE][+-]?\d*)?$'
            if not re.match(pattern, new_string):
                entry.stop_emission_by_name("insert-text")
                return True
            else:
                return False
        self.connect("insert-text", on_insert)

    def get_value(self):
        number_string = self.get_text()
        varifiacation = r'[-]?\d+([.]\d*)?([eE][+-]?\d+)?$'
        if not re.match(varifiacation, number_string):
            number_string += "0"
        pattern = "[.eE]"
        if re.search(pattern, number_string):
            return float(number_string)
        else:
            return int(number_string)
