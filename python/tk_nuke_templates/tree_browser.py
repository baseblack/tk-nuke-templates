"""
Copyright (c) 2012 Shotgun Software, Inc
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
from .browser_widget import BrowserWidget
from .browser_widget import ListItem
from .browser_widget import ListHeader
from .browser_widget import ListTree

class TreeProxyModel(QtGui.QSortFilterProxyModel):
    """
    Impliments a custom filtering operation on the tree model we have. The filter
    behaviour alters as the number of characters entered becomes more than 3.
    """

    def __init__(self):
        QtGui.QSortFilterProxyModel.__init__(self)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        index0 = self.sourceModel().index(sourceRow, 0, sourceParent)  # display text
        index2 = self.sourceModel().index(sourceRow, 2, sourceParent)  # display tags
        regex = self.filterRegExp()

        for i in xrange(0, self.sourceModel().rowCount(index0)):
            if self.filterAcceptsRow(i, index0):
                return True
        return regex.indexIn(self.sourceModel().data(index0)) != -1 or \
               regex.indexIn(self.sourceModel().data(index2)) != -1

class TreeBrowserWidget(BrowserWidget):

    def __init__(self, parent=None):
        BrowserWidget.__init__(self, parent)

        self.set_label("Published Templates")
        self.tree = self.add_item(ListTree)

    def get_data(self, model):
        filters = [['tank_type', 'is', {'type': 'TankType', 'name': 'Nuke Script Template', 'id':74}]]
        fields = ['code',
                  'sg_tags',
                  'version_number',
                  'entity',
                  'path',
                  'project.Project.name',
                  'project',
                  'description',
                  'tank_type',
                  'created_by']
        order = [{'field_name': 'project.Project.name', 'direction':'asc'},
                 {'field_name': 'code', 'direction':'asc'}]

        sg_data = self._app.shotgun.find('TankPublishedFile', filters, fields, order)
        root = model.invisibleRootItem()

        #########################################
        # <model>                               #
        # name | tags | type                    #
        #########################################

        pyModel = dict()  # easier than the data munging required to extract
                          # from the standardModel. We can discard this after
                          # the main model has been generated.

        bold = QtGui.QFont()
        bold.setWeight(QtGui.QFont.Bold)


        for template in sg_data:
            pName = template.get('project.Project.name')
            iName = template.get('code')
            try:
                eName = template.get('entity').get('name')
            except AttributeError:
                eName = None

            # Create or retrieve the StandardItem for the project.
            try:
                project = pyModel[pName].get('item')
            except:
                project = QtGui.QStandardItem("%s" % pName)
                project.setEditable(False)
                project.setSelectable(False)
                project.setData(bold, QtCore.Qt.FontRole)
                project.setForeground(QtCore.Qt.yellow)

                project_identifier = QtGui.QStandardItem('Project')
                project_identifier.setEditable(False)
                project_identifier.setSelectable(False)
                project_identifier.setForeground(QtCore.Qt.yellow)

                project_tags = QtGui.QStandardItem()
                project_tags.setEditable(False)
                project_tags.setSelectable(False)

                pyModel[pName] = {'item': project, 'children': {}}
                root.appendRow([project, project_identifier, project_tags])

            # Create or retrieve the StandardItem of the entity, if the template
            # is attached to one. If it is a show wide template then this will be
            # none.
            if eName:
                try:
                    entity = pyModel[pName]['children'][eName].get('item')
                except:
                    entity = QtGui.QStandardItem(eName)
                    entity.setEditable(False)
                    entity.setSelectable(False)
                    entity.setForeground(QtCore.Qt.yellow)

                    entity_identifier = QtGui.QStandardItem('Entity')
                    entity_identifier.setEditable(False)
                    entity_identifier.setSelectable(False)
                    entity_identifier.setForeground(QtCore.Qt.yellow)

                    entity_tags = QtGui.QStandardItem()
                    entity_tags.setEditable(False)
                    entity_tags.setSelectable(False)

                    pyModel[pName]['children'][eName] = {'item': entity, 'children': {}}
                    project.appendRow([entity, entity_identifier, entity_tags])

            # Create the StandardItem for the template
            item = QtGui.QStandardItem(iName)
            item.setData(template)
            item.setEditable(False)

            tags = QtGui.QStandardItem(template.get('sg_tags'))
            tags.setEditable(False)

            if eName:
                pyModel[pName]['children'][eName]['children'][iName] = {'item': item}
                entity.appendRow([item, QtGui.QStandardItem('Template'), tags])
            else:
                project.appendRow([item, QtGui.QStandardItem('Template'), tags])

        return model

    def process_result(self, result):
        self.proxy_model = TreeProxyModel()
        self.proxy_model.setSourceModel(result)

        self.tree.ui.view.setModel(self.proxy_model)
        self.tree.set_expanded(True)
        self.tree.set_animated(True)
        self.tree.set_column_width(0, 250)
        self.tree.set_hideColumn(1)
        self.tree.fit_view()

    def show_browser_header(self, state):
        self.ui.browser_header.setVisible(state)

    def _on_search_text_changed(self, text):
        """
        Overrides method on BrowserWidget. Custom search/filter for a TreeView.
        Utilises QSortFilterProxyModel
        """
        self.proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_model.setFilterRegExp(text.strip().replace(' ', '|'))
        self.proxy_model.invalidateFilter()
        self.tree.ui.view.expandAll()

