import json
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from editvaluewindow import EditValueWindow

from treenode import TreeNode

py_to_json = {
    r"<class 'NoneType'>": "Null",
    r"<class 'bool'>": "Boolean",
    r"<class 'int'>": "Number",
    r"<class 'float'>": "Number",
    r"<class 'str'>": "String",
    r"<class 'list'>": "Array",
    r"<class 'dict'>": "Object"
}

def get_json_type(value):
    return py_to_json[str(type(value))]

def test_path(model, path):
    if not path.up():
        return False, False
    if path.get_depth() == 0:
        return False, False

    iter = model.get_iter(path)
    #type = model.get_value(iter, 1)
    node = model.get_value(iter, 0)
    type = get_json_type(node.get_value())

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

        iter = self.get_iter(path)
        node = self[iter][0]
        edit_window = EditValueWindow(parent = window, parent_type = parent_type, node = node)
        response = edit_window.run()
        if response == Gtk.ResponseType.OK:
            self.set_value(iter, 0, edit_window.get_node())
        edit_window.destroy()

    def new_node(self, window, path):
        possible, key = test_path(self, path.copy())
        if not possible:
            return

        index = path.get_indices()[path.get_depth()-1]
        parent_path = path.copy()
        parent_path.up()
        parent_iter = self.get_iter(parent_path)

        self.insert(parent_iter, index, row = [TreeNode("", None)])
        self.edit_node(window, path)

    def import_node(self, iter, key, tree):
        type = get_json_type(tree)
        if type == "Array":
            new_iter = self.insert(iter, -1, row = [TreeNode(key, [])])
            for child in tree:
                self.import_node(new_iter, None, child)
        elif type == "Object":
            new_iter = self.insert(iter, -1, row = [TreeNode(key, {})])
            for child_key, child in tree.items():
                self.import_node(new_iter, child_key, child)
        else:
            self.insert(iter, -1, row = [TreeNode(key, tree)])

    def import_tree(self, tree):
        self.import_node(None, None, tree)

    def export_node(self, iter):
        node = self[iter][0]
        type = get_json_type(node.get_value())
        if type == "Array":
            array = []
            for i in range(0, self.iter_n_children(iter)):
                array.append(self.export_node(self.iter_nth_child(iter, i)))
            return array
        elif type == "Object":
            object = {}
            for i in range(0, self.iter_n_children(iter)):
                child_iter = self.iter_nth_child(iter, i)
                key = self[child_iter][0].get_key()
                object[key] = self.export_node(child_iter)
            return object
        else:
            return node.get_value()

    def export_tree(self):
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

        #self.store = JsonTreeStore(str, str, str, TreeValue.__gtype__,  TreeNode.__gtype__)
        self.store = JsonTreeStore(TreeNode.__gtype__)
        self.store.import_tree(None)

        self.treeview = Gtk.TreeView(
            enable_search=False,
            enable_tree_lines=True,
            headers_visible=False,
            model=self.store,
            reorderable=True,
        )
        self.add(self.treeview)

        cellRenderer = Gtk.CellRendererText(editable=False)
        #column = Gtk.TreeViewColumn(None, cellRenderer, text=4)
        column = Gtk.TreeViewColumn(None, cellRenderer, text=0)
        def f(column, cellRenderer, model, iter, x):
            #cellRenderer.set_property("text", model[iter][4].get_string())
            cellRenderer.set_property("text", model[iter][0].get_string())
        column.set_cell_data_func(cellRenderer, f)
        self.treeview.append_column(column)
        self.treeview.connect("button-press-event", self.mouse_clicked)
        self.treeview.connect("key-press-event", self.key_pressed)
        #targets = [('GTK_TREE_MODEL_ROW', 3, 0)]
        #self.treeview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, targets, Gdk.DragAction.MOVE)
        #self.treeview.enable_model_drag_dest(targets, Gdk.DragAction.MOVE)
        #self.treeview.connect("drag_data_get", self.drag_data_get_data)
        #self.treeview.connect("drag_data_received", self.drag_data_received_data)


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

            delete_item = Gtk.MenuItem.new_with_label("Delete")
            delete_item.show()
            if path == Gtk.TreePath():
                delete_item.set_sensitive(False)
            def delete(self):
                iter = store.get_iter(path)
                store.remove(iter)
            delete_item.connect("activate", delete)
            menu.attach(delete_item, 0, 1, 3, 4)

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
        elif key == "r":
            file_chooser = Gtk.FileChooserDialog("Open", self, Gtk.FileChooserAction.OPEN)
            file_chooser.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
            response = file_chooser.run()
            with open(file_chooser.get_filename(), 'r') as json_file:
                tree = json.loads(json_file.read())
            file_chooser.destroy()
            store = JsonTreeStore(TreeNode.__gtype__)
            tree = store.import_tree(tree)
            self.treeview.set_model(store)
            self.store = store
        elif key == "e":
            tree = store.export_tree()
            file_chooser = Gtk.FileChooserDialog("Save As", self, Gtk.FileChooserAction.SAVE)
            file_chooser.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
            response = file_chooser.run()
            with open(file_chooser.get_filename(), 'w') as json_file:
                json.dump(tree, json_file)
            file_chooser.destroy()
        elif key == "Delete":
            if not path == Gtk.TreePath():
                store.remove(iter)
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
