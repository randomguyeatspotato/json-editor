import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class JsonEditorWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="JSON Editor")

        self.store = Gtk.TreeStore(str)
        a = self.store.append(None, row=['a'])
        self.store.append(a, row=['x'])

        self.treeview = Gtk.TreeView(model=self.store)
        self.add(self.treeview)

        cellRenderer = Gtk.CellRendererText(editable=True)
        cellRenderer.connect("edited", self.on_field_edited)

        column = Gtk.TreeViewColumn(None, cellRenderer, text=0)
        self.treeview.append_column(column)

    def on_field_edited(self, cellRenderer, path, new_text):
        field_iter = self.store.get_iter(Gtk.TreePath(path))
        self.store.set_value(field_iter, 0, new_text)


win = JsonEditorWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
