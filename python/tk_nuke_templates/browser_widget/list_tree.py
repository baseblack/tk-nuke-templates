"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import nuke
import urlparse
import os
import urllib
import shutil
import sys

from PySide import QtCore, QtGui
from .ui.tree import Ui_Tree
from .list_base import ListBase



class ListTree(ListBase):

    def __init__(self, app, worker, parent=None):
        ListBase.__init__(self, app, worker, parent)

        # set up the UI
        self.ui = Ui_Tree()
        self.ui.setupUi(self)

        self._selected = False
        self._worker = worker
        self._worker_uid = None

        # spinner
        self._spin_icons = []
        self._spin_icons.append(QtGui.QPixmap(":/res/thumb_loading_1.png"))
        self._spin_icons.append(QtGui.QPixmap(":/res/thumb_loading_2.png"))
        self._spin_icons.append(QtGui.QPixmap(":/res/thumb_loading_3.png"))
        self._spin_icons.append(QtGui.QPixmap(":/res/thumb_loading_4.png"))

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect( self._update_spinner )
        self._current_spinner_index = 0

    def fit_view(self):
        self.ui.view.adjustSize()

    def set_column_width(self, column, width):
        self.ui.view.setColumnWidth(column, width)

    def set_animated(self, state):
        self.ui.view.setAnimated(state)

    def set_expanded(self, state):
        if state: self.ui.view.expandAll()
        else: self.ui.view.collapseAll()

    def set_hideColumn(self, column):
        self.ui.view.hideColumn(column)

    def expandAll(self):
        self.ui.view.expandAll()

    def supports_selection(self):
        return True

    def set_selected(self, status):
        self._selected = status

    def is_selected(self):
        return self._selected

    def set_details(self, txt):
        self.ui.details.setText(txt)

    def get_details(self):
        #used by search
        return "foobar"

    def set_thumbnail(self, url):
        pass

    ############################################################################################
    # internal stuff

    def _update_spinner(self):
        """
        Animate spinner icon
        """
        self.ui.thumbnail.setPixmap(self._spin_icons[self._current_spinner_index])
        self._current_spinner_index += 1
        if self._current_spinner_index == 4:
            self._current_spinner_index = 0

    def _download_thumbnail(self, data):
        return

    def _on_worker_task_complete(self, uid, data):
        if uid != self._worker_uid:
            return

        # stop spin
        self._timer.stop()


