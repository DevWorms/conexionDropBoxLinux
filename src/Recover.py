#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk

pygtk.require('2.0')
import gobject
import gtk

#   columns
(
    DATE_NAME_COLUMN,
    SIZE_COLUMN,
    TYPE_COLUMN,
    DOWNLOAD_COLUMN,
    VISIBLE_COLUMN,
    NUM_COLUMNS,
    WORLD_COLUMN,
    DAVE_COLUMN
) = range(8)

#   tree data
january = \
    [
        ["Respaldo 1.bak", True, True, True]
    ]

february = \
    [
        ["Respaldo 2.bak", True, True, True]
    ]

march = \
    [
        ["Respaldo 1.bak", True, True, True],
        ["Respaldo 1.bak", True, True, True]
    ]
april = \
    [
        ["Respaldo 1.bak", True, True, True]
    ]

may = \
    [
        ["Respaldo 3.bak", True, True, True],
        ["Respaldo 4.bak", True, True, True]
    ]

june = \
    [
        ["Respaldo 1.bak", True, True, True]
    ]

july = \
    [
        ["Respaldo 1.bak", True, True, True]
    ]

august = \
    [
        ["Respaldo 5.bak", True, True, True],
        ["Respaldo 6.bak", True, True, True],
        ["Respaldo 8.bak", True, True, True]
    ]

september = \
    [
        ["Respaldo 10.bak", True, True, True]
    ]

october = \
    [
        ["Respaldo 11.bak", True, True, True],
        ["Respaldo 12.bak", True, True, True]
    ]

november = \
    [
        ["Respaldo 14.bak", True, True, True]
    ]

december = \
    [
        ["Respaldo 21.bak", True, True, True]
    ]

months = \
    [
        ["Enero", False, False, False, False, False, False, january],
        ["Febrero", False, False, False, False, False, False, february],
        ["Marzo", False, False, False, False, False, False, march],
        ["Abril", False, False, False, False, False, False, april],
        ["Mayo", False, False, False, False, False, False, may],
        ["Junio", False, False, False, False, False, False, june],
        ["Julio", False, False, False, False, False, False, july],
        ["Agosto", False, False, False, False, False, False, august],
        ["Septiembre", False, False, False, False, False, False, september],
        ["Octubre", False, False, False, False, False, False, october],
        ["Noviembre", False, False, False, False, False, False, november],
        ["Diciembre", False, False, False, False, False, False, december]
    ]

years = \
    [
        ["2015", months],
        ["2016", months],
        ["2017", months]
    ]


class TreeStoreDemo(gtk.Window):
    def __init__(self, parent=None):
        gtk.Window.__init__(self)
        try:
            self.set_screen(parent.get_screen())
        except AttributeError:
            self.connect('destroy', lambda *w: gtk.main_quit())
        self.set_title("Recuperar Respaldo")
        self.set_default_size(650, 400)
        self.set_border_width(8)

        vbox = gtk.VBox(False, 8)
        self.add(vbox)

        label = gtk.Label("Selecciona un respaldo")
        vbox.pack_start(label, False, False)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox.pack_start(sw)

        # create model
        model = self.__create_model()

        # create treeview
        treeview = gtk.TreeView(model)
        treeview.set_rules_hint(True)

        self.__add_columns(treeview)

        sw.add(treeview)

        # expand all rows after the treeview widget has been realized
        treeview.connect('realize', lambda tv: tv.expand_all())

        self.show_all()

    def __create_model(self):

        # create tree store
        model = gtk.TreeStore(
            gobject.TYPE_STRING,
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_BOOLEAN,
            gobject.TYPE_BOOLEAN)

        # add data to the tree store
        for year in years:
            iter = model.append(None)
            model.set(iter,
                DATE_NAME_COLUMN, year[DATE_NAME_COLUMN]
            )
            for month in months:
                month_iter = model.append(iter)
                model.set(month_iter,
                          DATE_NAME_COLUMN, month[DATE_NAME_COLUMN]
                          )

                # add children
                for backup in month[-1]:
                    child_iter = model.append(month_iter);
                    model.set(child_iter,
                              DATE_NAME_COLUMN, backup[DATE_NAME_COLUMN],
                              SIZE_COLUMN, backup[SIZE_COLUMN],
                              TYPE_COLUMN, backup[TYPE_COLUMN],
                              DOWNLOAD_COLUMN, backup[DOWNLOAD_COLUMN],
                              VISIBLE_COLUMN, True,
                              )

        return model

    def on_item_toggled(self, cell, path_str, model):

        # get selected column
        column = cell.get_data('column')

        # get toggled iter
        iter = model.get_iter_from_string(path_str)
        toggle_item = model.get_value(iter, column)

        # do something with the value
        toggle_item = not toggle_item

        # set new value
        model.set(iter, column, toggle_item)

    def __add_columns(self, treeview):
        model = treeview.get_model()

        # column for holiday names
        renderer = gtk.CellRendererText()
        renderer.set_property("xalign", 0.0)

        column = gtk.TreeViewColumn("Fecha", renderer, text=DATE_NAME_COLUMN)
        # column = gtk_tree_view_get_column(GTK_TREE_VIEW(treeview), col_offset - 1);
        column.set_clickable(True)

        treeview.append_column(column)

        # alex column */
        renderer = gtk.CellRendererText()
        renderer.set_property("xalign", 0.0)

        if SIZE_COLUMN:
            column = gtk.TreeViewColumn("Tamaño", renderer, text=SIZE_COLUMN)
        else:
            column = gtk.TreeViewColumn("Tamaño", renderer, text = "")

        # set this column to a fixed sizing(of 50 pixels)
        # column = gtk_tree_view_get_column(GTK_TREE_VIEW(treeview), col_offset - 1);
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(100)
        column.set_clickable(True)

        treeview.append_column(column)

        # havoc column
        renderer = gtk.CellRendererToggle();
        renderer.set_property("xalign", 0.0)
        renderer.set_data("column", DOWNLOAD_COLUMN)

        renderer.connect("toggled", self.on_item_toggled, model)

        column = gtk.TreeViewColumn("Tipo", renderer, active=TYPE_COLUMN,
                                    visible=VISIBLE_COLUMN)

        # column = treeview.get_column(col_offset - 1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(50)
        column.set_clickable(True)

        treeview.append_column(column)

        # tim column
        renderer = gtk.CellRendererToggle();
        renderer.set_property("xalign", 0.0)
        renderer.set_data("column", DOWNLOAD_COLUMN)

        renderer.connect("toggled", self.on_item_toggled, model)

        column = gtk.TreeViewColumn("Descargar", renderer, active=DOWNLOAD_COLUMN,
                                    visible=VISIBLE_COLUMN)

        # column = treeview.get_column(col_offset - 1)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        column.set_fixed_width(50)
        column.set_clickable(True)

        treeview.append_column(column)


def main():
    TreeStoreDemo()
    gtk.main()


if __name__ == '__main__':
    main()
