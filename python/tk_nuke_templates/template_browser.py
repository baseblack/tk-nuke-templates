
"""
Copyright (c) 2012 Shotgun Software, Inc
----------------------------------------------------
"""
import nuke
import tank
import os
import sys
import threading

from PySide import QtCore, QtGui
from .browser_widget import BrowserWidget
from .browser_widget import ListItem
from .browser_widget import ListHeader

class TemplateBrowserWidget(BrowserWidget):

    def __init__(self, parent=None):
        BrowserWidget.__init__(self, parent)

        self.set_label("Details")
        self.enable_search(False)

    def get_data(self, data):
        sg_data = []
        template_data = self._app.shotgun.find("TankPublishedFile",
                                               [ ["id", "is", data["id"]] ],
                                               ["name", "path", "description", "created_by", "created_at", "sg_tags"])

        return template_data

    def process_result(self, result):

        if not result:
            self.set_message("No matching items found!")
            return

        for item in result:
            print item

            i = self.add_item(ListHeader)
            i.set_title("Release information for %s" % item['name'])
            i = self.add_item(ListItem)

            details = []
            details.append("<b>Template: %s</b>" % item.get("name"))
            details.append("Created By: %s" % item.get("created_by").get("name"))
            details.append("Date Created: %s" % item.get("created_at"))

            i.set_details("<br>".join(details))
            i.sg_data = item
            if item.get("image"):
                i.set_thumbnail(item.get("image"))
            else:
                # first try to get the image from the published file. After that grab the creator instead.
                try:
                    img_data = self._app.shotgun.find_one("HumanUser", [["id","is", item.get("created_by").get("id")]], ['image'])
                except:
                    img_data = self._app.shotgun.find_one("ApiUser", [["id","is", item.get("created_by").get("id")]], ['image'])
                if img_data:
                    i.set_thumbnail(img_data.get("image"))

            i = self.add_item(ListHeader)
            i.set_title("Description")
            i = self.add_item(ListItem)
            i.ui.thumbnail.setVisible(False)
            i.sg_data = item

            if item.get("description"):
                i.set_details(item.get("description"))
            else:
                i.set_details("<b>No comments available</b>")

            i = self.add_item(ListHeader)
            i.set_title("Additional metadata")
            i = self.add_item(ListItem)
            i.ui.thumbnail.setVisible(False)
            i.sg_data = item

            if item.get("sg_tags"):
                details = []
                details.append("<b>Tags: %s</b>" % item.get("sg_tags"))
                #...
                i.set_details("<br>".join(details))
            else:
                i.set_details("<b>No additional metadata</b>")
