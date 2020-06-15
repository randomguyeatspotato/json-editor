import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class JsonEditorWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="JSON Editor")

        self.store = Gtk.TreeStore(str, int)
        a = self.store.append(None, row=['a', 0])
        self.store.append(a, row=['x', 1])
        self.store.append(a, row=['y', 2])

        self.treeview = Gtk.TreeView(
            enable_tree_lines=True,
            headers_visible=True,
            model=self.store,
            reorderable=True,
        )
        self.add(self.treeview)

        cellRenderer = Gtk.CellRendererText(editable=True)
        cellRenderer.connect("edited", self.on_field_edited)

        column1 = Gtk.TreeViewColumn("Tree", cellRenderer, text=0)
        self.treeview.append_column(column1)
        column2 = Gtk.TreeViewColumn("Value", cellRenderer, text=1)
        self.treeview.append_column(column2)

        self.treeview.connect("key-press-event", self.key_pressed)

    def on_field_edited(self, cellRenderer, path, new_text):
        field_iter = self.store.get_iter(Gtk.TreePath(path))
        self.store.set_value(field_iter, 0, new_text)

    def key_pressed(self, treeview, event):
        self.treeview.expand_row(self.treeview.get_cursor()[0], False)
        print("key pressed")
        #if (block highlighted)
            #if keyname == 'Tab':
            #else keyname == 'Return':
        #else
        #highlight first block

#self.dataTableTreeView.connect("key-press-event", self.onTreeNavigateKeyPress)

win = JsonEditorWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
