import gi
import json

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

root = {'first': 1, 'second': "hello"}

#print(json.dumps(root))

json_types = {
    "Null": type(None),
    "Boolean": bool,
    "Number": int,
    "String": str,
    "Array": list,
    "Object": dict}

class EditValueWindow(Gtk.Dialog):
    def __init__(self, parent, parent_type):
        #Gtk.DialogFlags.MODAL
        Gtk.Dialog.__init__(self, "Edit Node", parent, modal = True)

        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Ok", Gtk.ResponseType.OK)

        self.set_default_size(200, 100)
        area = self.get_content_area()
        area.add(Gtk.Label(label = "Node Definition"))
        node_box = Gtk.HBox()

        if parent_type == "Object" or True:
            key = Gtk.Entry()
            self.key = key
            key_box = Gtk.VBox()
            key_box.pack_start(Gtk.Label(label = "Key"), True, True, 0)
            key_box.pack_start(key, True, True, 0)
            node_box.pack_start(key_box, True, True, 0)

        type_store = Gtk.ListStore(str)
        for k in json_types:
            type_store.append([k])
        type_select = Gtk.ComboBox.new_with_model_and_entry(type_store)
        type_select.set_entry_text_column(0)
        type_select.set_active(0)
        self.type_select = type_select
        type_box = Gtk.VBox()
        type_box.pack_start(Gtk.Label(label = "Type"), True, True, 0)
        type_box.pack_start(type_select, True, True, 0)
        node_box.pack_start(type_box, True, True, 0)

        value_stack = Gtk.Stack()
        self.value_stack = value_stack
        type_select.connect("changed", self.type_changed)

        null_page = Gtk.Label()
        null_page.set_text("null")
        value_stack.add_titled(null_page, "Null", "Null")


        boolean_store = Gtk.ListStore(str)
        boolean_store.append(["false"])
        boolean_store.append(["true"])
        boolean_select = Gtk.ComboBox.new_with_model_and_entry(boolean_store)
        #boolean_select.connect("changed", )
        boolean_select.set_entry_text_column(0)
        boolean_select.set_active(0)
        value_stack.add_titled(boolean_select, "Boolean", "Boolean")

        c = Gtk.Entry()
        c.set_text("Number")
        value_stack.add_titled(c, "Number", "Number")

        d = Gtk.Entry()
        d.set_text("String")
        value_stack.add_titled(d, "String", "String")

        array_page = Gtk.Label()
        array_page.set_text("[ ]")
        value_stack.add_titled(array_page, "Array", "Array")

        object_page = Gtk.Label()
        object_page.set_text("{ }")
        value_stack.add_titled(object_page, "Object", "Object")

        value_box = Gtk.VBox()
        value_box.pack_start(Gtk.Label(label = "Value"), True, True, 0)
        value_box.pack_start(value_stack, True, True, 0)
        node_box.pack_start(value_box, True, True, 0)

        area.add(node_box)



        #grid = Gtk.Grid()
        #grid.attach(Gtk.Label("Key"  ), 0, 0, 1, 1)
        #grid.attach(Gtk.Label("Type" ), 1, 0, 1, 1)
        #grid.attach(Gtk.Label("Value"), 2, 0, 1, 1)
        #grid.attach(key               , 0, 1, 1, 1)
        #grid.attach(type_select       , 1, 1, 1, 1)
        #grid.attach(value_stack       , 2, 1, 1, 1)

        #area.add(grid)

        self.show_all()

    def type_changed(self, combo):
        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        type = model[tree_iter][0]

        self.value_stack.set_visible_child_name(type)

    def get_node_key(self):
        return self.key.get_text()

    def get_node_type(self):
        index = self.type_select.get_active()
        model = self.type_select.get_model()
        iter = model.iter_nth_child(None, index)
        return model.get_value(iter, 0)

    def get_node_value():
        return ""

    def to_string(self):
        string = ""
        if self.key:
            string += self.get_node_key()
            string += ": "

        #type = self.get_nodetype()

        child = self.value_stack.get_visible_child()
        child_type = type(child)
        if child_type == Gtk.Label:
            string += child.get_text()
        elif child_type == Gtk.ComboBox:
            string += ["false", "true"][child.get_active()]
        elif child_type == Gtk.Entry:
            if self.get_node_type() == "String":
                string += '"'
                string += child.get_text()
                string += '"'
            else:
                string += child.get_text()


        return string

        #def row_to_string(treestore, iter, parentiter, value)

        #    k = treestore.get_value(iter, 0)
        #    t = treestore.get_value(iter, 1)
        #    ot = type(value)
        #    if ot == list:
        #        s = "[]"
        #   elif ot == dict:
        #       s = "{}"
        #   else:
        #       s = str(value)
        #   pt = treestore.get_value(parentiter, 1)
        #   if pt == list:
        #       o = s
        #   elif pt == dict:
        #       o = '"' + k '": ' + s
        #   else:
        #       o =


class JsonEditorWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="JSON Editor")

        self.store = Gtk.TreeStore(str, str, str)
        a = self.store.append(None, row=['a', 'string', 'hello'])

        self.treeview = Gtk.TreeView(
            enable_search=False,
            enable_tree_lines=True,
            headers_visible=True,
            model=self.store,
            reorderable=True,
        )
        self.add(self.treeview)

        cellRenderer = Gtk.CellRendererText(editable=False)
        cellRenderer.connect("edited", self.on_field_edited)
        column = Gtk.TreeViewColumn(None, cellRenderer, text=2)
        self.treeview.append_column(column)
        self.treeview.connect("button-press-event", self.mouse_clicked)
        self.treeview.connect("key-press-event", self.key_pressed)

    def on_field_edited(self, cellRenderer, path, new_text):
        field_iter = self.store.get_iter(Gtk.TreePath(path))
        self.store.set_value(field_iter, 0, new_text)

    def mouse_clicked(self, treeview, event):
        button = event.button

        if button == 1:
            #GDK_2BUTTON_PRESS = 5 find the actual reference
            if event.type == 5:
                parent_type = "Array"
                edit_window = EditValueWindow(parent = self, parent_type = parent_type)
                response = edit_window.run()
                if response == Gtk.ResponseType.OK:
                    print(edit_window.get_node_key())
                    print(edit_window.get_node_type())
                    cursor = self.treeview.get_cursor()[0]
                    iter = self.store.get_iter(cursor)
                    self.store.set_value(iter, 2, edit_window.to_string())
                edit_window.destroy()
        elif button == 3:
            menu = Gtk.Menu()
            menu.popup_at_pointer(event)

        #previous_curosor = cursor


    def key_pressed(self, treeview, event):
        key = Gdk.keyval_name(event.keyval)
        cursor = self.treeview.get_cursor()[0]
        iter = self.store.get_iter(cursor)
        #print(cursor, cursor.get_indices())
        if key == "Right":
            if self.treeview.row_expanded(cursor):
                self.treeview.collapse_row(cursor)
            else:
                self.treeview.expand_row(cursor, False)
        elif key == "i":
            self.store.insert_before(None, iter, [' ', ' ', 'new'])
        elif key == "o":
            self.store.insert_after(None, iter, [' ', ' ', 'new'])
        elif key == "p":
            self.store.prepend(iter, [' ', ' ', 'new'])
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
