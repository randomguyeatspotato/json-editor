import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class JsonEditorWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="JSON Editor")

        self.store = Gtk.TreeStore(str, int)
        a = self.store.append(None, row=['a', 0])
        self.store.append(a, row=['x', 1])
        self.store.append(a, row=['y', 2])

        self.treeview = Gtk.TreeView(
            enable_search=False,
            enable_tree_lines=True,
            headers_visible=True,
            model=self.store,
            reorderable=True,
        )
        self.add(self.treeview)

        cellRenderer = Gtk.CellRendererText(editable=True)
        cellRenderer.connect("edited", self.on_field_edited)

        cellRenderer2 = Gtk.CellRendererText(editable=False)

        column1 = Gtk.TreeViewColumn("Tree", cellRenderer, text=0)
        self.treeview.append_column(column1)
        column2 = Gtk.TreeViewColumn("Value", cellRenderer2, text=1)
        self.treeview.append_column(column2)

        self.treeview.connect("button-press-event", self.mouse_clicked)
        self.treeview.connect("key-press-event", self.key_pressed)

    def on_field_edited(self, cellRenderer, path, new_text):
        field_iter = self.store.get_iter(Gtk.TreePath(path))
        self.store.set_value(field_iter, 0, new_text)

    def mouse_clicked(self, treeview, event):
        print("mouse clicked")
        for o in vars(event):
            print(o)

    def key_pressed(self, treeview, event):
        key = Gdk.keyval_name(event.keyval)
        cursor = self.treeview.get_cursor()[0]
        iter = self.store.get_iter(cursor)

        if key == "Right":
            if self.treeview.row_expanded(cursor):
                self.treeview.collapse_row(cursor)
            else:
                self.treeview.expand_row(cursor, False)
        elif key == "i":
            self.store.insert_before(None, iter, [' ', 0])
        elif key == "o":
            self.store.insert_after(None, iter, [' ', 0])
        elif key == "p":
            self.store.prepend(iter, [' ', 0])
        else:
            print("key pressed", key)
        #if (block highlighted)
            #if keyname == 'Tab':
            #else keyname == 'Return':
        #else
        #highlight first block

win = JsonEditorWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
