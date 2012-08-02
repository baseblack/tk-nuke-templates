
"""
Copyright (c) 2012 Baseblack London, Ltd
----------------------------------------------------
"""
import nuke
import tank
import os
import sys
import threading
import collections
import re

from PySide import QtCore, QtGui
from .ui.search_dialog import Ui_Dialog

class SearchDialog(QtGui.QDialog):
    """
    Blatant plagarisation and attempt at keeping code base for this app similar
    to Shotgun's official App design.
    """

    def __init__(self, app):
        QtGui.QDialog.__init__(self)
        self._app = app

        self._settings = QtCore.QSettings("Baseblack Ltd", "tk-nuke-templates")

        # internal data structures
        self.__files = []
        self.__filters = {'name': set(), 'entity': set(), 'tag': set()}

        # model data structure we're going to store all our results on.
        self.model = QtGui.QStandardItemModel()

        # set up the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.left_view.set_app(self._app)
        self.ui.right_view.set_app(self._app)
        self.ui.right_view.set_message("Please select a template in the listing to the left.")

        self.ui.left_view.tree.ui.view.clicked[QtCore.QModelIndex].connect(self.set_selected_template)
        self.ui.refresh.clicked.connect(self.refresh_ui)
        self.ui.importButton.clicked.connect(self.import_selection)

        self.refresh_ui()

    def refresh_ui(self):
        """
        Button widget accessor
        """
        self.ui.right_view.clear()
        self.ui.right_view.set_message("Please select a template in the listing to the left.")

        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Filename', 'Type', 'Tags'])
        self.ui.left_view.load(self.model)

    def set_selected_template(self, proxy_index):
        self.ui.right_view.clear()
        source_index = self.ui.left_view.proxy_model.mapToSource(proxy_index)
        self.selected_item = self.model.itemFromIndex(source_index)

        # WARNING - FUCKHACKERY INBOUND #
        try:
            id = self.selected_item.data().get('id')
            self.ui.right_view.load({'id': int(id)})
        except AttributeError as err:
            self.ui.right_view.clear()
            self.ui.right_view.set_message("Not a template, please select a template in the listing to the left.")

    def import_selection(self):
        if hasattr(self, 'selected_item'):
            print self.selected_item.data()
            template_path = self.selected_item.data().get('path').get('local_path')

            for n in nuke.allNodes():
                if n.Class()=='Viewer':
                    x = n.xpos()
                    y = n.ypos()

            nuke.scriptReadFile(template_path)
            nuke.selectConnectedNodes()
            nodes = nuke.selectedNodes()

            for n in nodes:
                n.setXYpos(x, y)

            for n in nodes:
                n.autoplace()

            nuke.message('Template imported!')
            self.close()
