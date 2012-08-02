"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import nukescripts
import tempfile
import nuke
import os
import platform
import sys
import uuid
import shutil


class AppHandler(object):
    """
    Handles the startup of the UIs, wrapped so that
    it works nicely in batch mode.
    """

    def __init__(self, app):
        self._app = app

    def search_dialog(self):
        from .search_dialog import SearchDialog

        nuke._tank_templates_search = SearchDialog(self._app)
        nuke._tank_templates_search.exec_()

    def publish_dialog(self):
        from .publish_dialog import PublishDialog

        nuke._tank_templates_publish = PublishDialog(self._app)
        nuke._tank_templates_publish.exec_()

