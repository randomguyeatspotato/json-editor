import json

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from treenode import TreeNode

from entryfieldnone import EntryFieldNone
from entryfieldboolean import EntryFieldBoolean
from entryfieldnumber import EntryFieldNumber
from entryfieldstring import EntryFieldString
from entryfieldlist import EntryFieldList
from entryfielddictionary import EntryFieldDictionary

json_types = [
    "Null",
    "Boolean",
    "Number",
    "String",
    "Array",
    "Object"
    ]

py_to_json = {
    r"<class 'NoneType'>": "Null",
    r"<class 'bool'>": "Boolean",
    r"<class 'int'>": "Number",
    r"<class 'float'>": "Number",
    r"<class 'str'>": "String",
    r"<class 'list'>": "Array",
    r"<class 'dict'>": "Object"
}

json_to_entry_field = {
    "Null": EntryFieldNone,
    "Boolean": EntryFieldBoolean,
    "Number": EntryFieldNumber,
    "String": EntryFieldString,
    "Array": EntryFieldList,
    "Object": EntryFieldDictionary
}

TypeType = type(type(None))
def to_json(value):
    if type(value) == TypeType:
        return py_to_json[str(value)]
    else:
        return json.dumps(value)

class EditValueWindow(Gtk.Dialog):
    def __init__(self, parent, parent_type, node):
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

        active = 0
        node_value = node.get_value()
        node_type = to_json(type(node_value))
        type_store = Gtk.ListStore(str)

        value_stack = Gtk.Stack()
        self.value_stack = value_stack

        for k, entry_class in json_to_entry_field.items():
            entry = entry_class(to_json)
            value_stack.add_titled(entry, k, k)
            type_store.append([k])
            if k == node_type:
                active = type_store.iter_n_children() - 1
                entry.set_value(node_value)

        type_select = Gtk.ComboBox.new_with_model_and_entry(type_store)
        type_select.set_entry_text_column(0)
        self.type_select = type_select
        type_box = Gtk.VBox()
        type_box.pack_start(Gtk.Label(label = "Type"), True, True, 0)
        type_box.pack_start(type_select, True, True, 0)
        node_box.pack_start(type_box, True, True, 0)


        value_box = Gtk.VBox()
        value_box.pack_start(Gtk.Label(label = "Value"), True, True, 0)
        value_box.pack_start(value_stack, True, True, 0)
        node_box.pack_start(value_box, True, True, 0)

        area.add(node_box)
        type_select.connect("changed", self.type_changed)
        self.show_all()
        type_select.set_active(active)

    def type_changed(self, combo):
        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        type = model[tree_iter][0]
        self.value_stack.set_visible_child_name(type)

    def get_node(self):
        key = None
        if hasattr(self, 'key'):
            key = self.key.get_text()
        combo = self.type_select
        tree_iter = combo.get_active_iter()
        model = combo.get_model()
        type = model[tree_iter][0]

        child = self.value_stack.get_visible_child()
        return TreeNode(key, child.get_value())
