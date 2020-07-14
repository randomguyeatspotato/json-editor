import gi
import json

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

#root = {'first': 1, 'second': "hello"}
#print(json.dumps(root))

json_types = {
    "Null": type(None),
    "Boolean": bool,
    "Number": int,
    "String": str,
    "Array": list,
    "Object": dict}

class TreeValue(GObject.GObject):
    def __init__(self, value):
        GObject.GObject.__init__(self)
        self.value = value

    def get_value(self):
        return self.value

GObject.type_register(TreeValue)

class EditValueWindow(Gtk.Dialog):
    def __init__(self, parent, parent_type):
        Gtk.Dialog.__init__(self, "Edit Node", parent, modal = True)

        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.add_button("Ok", Gtk.ResponseType.OK)

        self.set_default_size(200, 100)
        area = self.get_content_area()
        area.add(Gtk.Label(label = "Node Definition"))
        node_box = Gtk.HBox()

        if parent_type == "Object":
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
        self.show_all()

    def type_changed(self, combo):
        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        type = model[tree_iter][0]

        self.value_stack.set_visible_child_name(type)

    def get_node_key(self):
        if hasattr(self, 'key'):
            return self.key.get_text()
        else:
            return ""

    def get_node_type(self):
        index = self.type_select.get_active()
        model = self.type_select.get_model()
        iter = model.iter_nth_child(None, index)
        return model.get_value(iter, 0)

    def get_node_value(self):
        type = self.get_node_type()
        child = self.value_stack.get_visible_child()
        if type == "Null":
            return TreeValue(None)
        elif type == "Boolean":
            return TreeValue([False, True][child.get_active()])
        elif type == "Number":
            return TreeValue(0)
        elif type == "String":
            return TreeValue(child.get_text())
        elif type == "Array":
            return TreeValue([])
        elif type == "Object":
            return TreeValue({})

    def to_string(self):
        string = ""
        if hasattr(self, 'key'):
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

def test_path(model, path):
    if not path.up():
        return False, False
    if path.get_depth() == 0:
        return False, False

    iter = model.get_iter(path)
    type = model.get_value(iter, 1)

    if type == "Array":
        possible = True
        key = False
    elif type == "Object":
        possible = True
        key = True
    else:
        possible = False
        key = False
    return possible, key

class JsonTreeStore(Gtk.TreeStore):
    def do_row_drop_possible(self, dest_path, selection_data):
        valid, model, path = Gtk.tree_get_row_drag_data(selection_data)
        path = dest_path.copy()
        possible, key = test_path(model, path)
        #add popup for key/no key
        return possible

    def edit_node(self, window, path):
        possible, key = test_path(self, path.copy())
        parent_type = ""
        if possible:
            if key:
                parent_type = "Object"
            else:
                parent_type = "Array"

        edit_window = EditValueWindow(parent = window, parent_type = parent_type)
        response = edit_window.run()
        if response == Gtk.ResponseType.OK:
            iter = self.get_iter(path)
            self.set_value(iter, 0, edit_window.get_node_key())
            self.set_value(iter, 1, edit_window.get_node_type())
            self.set_value(iter, 2, edit_window.to_string())
            self.set_value(iter, 3, edit_window.get_node_value())
        edit_window.destroy()

    def new_node(self, window, path):
        possible, key = test_path(self, path.copy())
        if not possible:
            return

        index = path.get_indices()[path.get_depth()-1]
        parent_path = path.copy()
        parent_path.up()
        parent_iter = self.get_iter(parent_path)

        self.insert(parent_iter, index)
        self.edit_node(window, path)

    def export_node(self, iter):
        type = self[iter][1]
        if type == "Array":
            array = []
            for i in range(0, self.iter_n_children(iter)):
                array.append(self.export_node(self.iter_nth_child(iter, i)))
            return array
        elif type == "Object":
            object = {}
            for i in range(0, self.iter_n_children(iter)):
                child_iter = self.iter_nth_child(iter, i)
                key = self[child_iter][0]
                object[key] = self.export_node(child_iter)
            return object
        else:
            return self[iter][3].get_value()

    def export(self):
        iter = self.get_iter(Gtk.TreePath())
        return self.export_node(iter)

class JsonEditorWindow(Gtk.Window):

    def drag_data_get_data(self, treeview, context, selection, target, etime):
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()
        path = model.get_path(iter)
        Gtk.tree_set_row_drag_data(selection, model, path)
        #treeselection = treeview.get_selection()
        #model, iter = treeselection.get_selected()
        #print(model, iter)
        #model = Json tree store
        #get the value of a column
        #data = model.get_value(iter, 2)
        #print(data)
        #a = selection.target
        #a = selection.get_target()
        #a = selection.get_data_type()
        #a = type(data)
        #print(a)
        #selection.set(a, 8, data)

        #print(dir(type(selection)))
        #selection.tree_set_row_drag_data(model, model.get_path(iter))

    #def drag_data_received_data(self, treeview, context, x, y, selection, info, etime):
        #valid, model, path = Gtk.tree_get_row_drag_data(selection)
        #print(valid, model, path)
#        treeselection = treeview.get_selection()
#        model, iter = treeselection.get_selected()
#        print(model, iter)
#        model = treeview.get_model()
#        #data = selection.get_text()
#        data = selection.get_data()
#        drop_info = treeview.get_dest_row_at_pos(x, y)
#        if drop_info:
#            path, position = drop_info
#            iter = model.get_iter(path)
#            print(iter)
#            print(type(iter))
#            model.insert_after(iter, [data])
#        else:
#            model.append([data])
#        if context.action == Gdk.DragAction.MOVE:
#            context.finish(True, True, etime)
#        return


    def __init__(self):
        Gtk.Window.__init__(self, title="JSON Editor")

        self.set_default_size(800, 600)

        self.store = JsonTreeStore(str, str, str, TreeValue.__gtype__)
        self.store.append(None)
        self.store.edit_node(self, Gtk.TreePath())

        self.treeview = Gtk.TreeView(
            enable_search=False,
            enable_tree_lines=True,
            headers_visible=False,
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
        #targets = [('GTK_TREE_MODEL_ROW', 3, 0)]
        #self.treeview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, targets, Gdk.DragAction.MOVE)
        #self.treeview.enable_model_drag_dest(targets, Gdk.DragAction.MOVE)
        #self.treeview.connect("drag_data_get", self.drag_data_get_data)
        #self.treeview.connect("drag_data_received", self.drag_data_received_data)

    def on_field_edited(self, cellRenderer, path, new_text):
        field_iter = self.store.get_iter(Gtk.TreePath(path))
        self.store.set_value(field_iter, 0, new_text)

    def mouse_clicked(self, treeview, event):
        button = event.button
        p = treeview.get_path_at_pos(event.x, event.y)
        if p == None:
            return
        path = p[0]
        store = self.store
        model = treeview.get_model()

        if button == 1:
            #GDK_2BUTTON_PRESS = 5 find the actual reference
            if event.type == 5:
                store.edit_node(self, path)
        elif button == 3:
            window = self
            path_copy = path.copy()
            siblings, sibling_keys = test_path(model, path_copy)
            child_path = path.copy()
            child_path.down()
            child, child_key = test_path(model, child_path)

            menu = Gtk.Menu()

            insert_item = Gtk.MenuItem.new_with_label("Insert")
            insert_item.show()
            insert_item.set_sensitive(siblings)
            def insert(self):
                store.new_node(window, path)
            insert_item.connect("activate", insert)
            menu.attach(insert_item, 0, 1, 0, 1)

            append_item = Gtk.MenuItem.new_with_label("Apend")
            append_item.show()
            append_item.set_sensitive(siblings)
            def append(self):
                path.next()
                store.new_node(window, path)
            append_item.connect("activate", append)
            menu.attach(append_item, 0, 1, 1, 2)

            insert_child_item = Gtk.MenuItem.new_with_label("Insert Child")
            insert_child_item.show()
            insert_child_item.set_sensitive(child)
            def insert_child(self):
                path.down()
                store.new_node(window, path)
            insert_child_item.connect("activate", insert_child)
            menu.attach(insert_child_item, 0, 1, 2, 3)

            menu.popup_at_pointer(event)

        #previous_curosor = cursor


    def key_pressed(self, treeview, event):
        key = Gdk.keyval_name(event.keyval)
        path = self.treeview.get_cursor()[0]
        store = self.store
        iter = store.get_iter(path)

        if key == "Right":
            if self.treeview.row_expanded(path):
                self.treeview.collapse_row(path)
            else:
                self.treeview.expand_row(path, False)
        elif key == "i":
            store.new_node(self, path)
        elif key == "o":
            path.next()
            store.new_node(self, path)
        elif key == "p":
            path.down()
            store.new_node(self, path)
        elif key == "e":
            tree = store.export()
            file_chooser = Gtk.FileChooserDialog("Save As", self, Gtk.FileChooserAction.SAVE)
            file_chooser.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
            response = file_chooser.run()
            with open(file_chooser.get_filename(), 'w') as json_file:
                json.dump(tree, json_file)
            file_chooser.destroy()
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
