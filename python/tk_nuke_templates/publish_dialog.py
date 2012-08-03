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
from .ui.publish_dialog import Ui_Dialog

class ListProxyModel(QtGui.QSortFilterProxyModel):
    """
    Impliments a custom filtering operation on the tree model we have. The filter
    behaviour alters as the number of characters entered becomes more than 3.
    """

    def __init__(self):
        QtGui.QSortFilterProxyModel.__init__(self)
        self.filter_index = 2

    def filterAcceptsRow(self, sourceRow, sourceParent):
        index3 = self.sourceModel().index(sourceRow, self.filter_index, sourceParent)  # project name
        regex = self.filterRegExp()

        return regex.indexIn(self.sourceModel().data(index3)) != -1

class PublishDialog(QtGui.QDialog):
    """
    I'd rather have click throughs to build the release parameters. But time is
    lacking... so combo boxes and inline shotgun calls are order of the day.
    """

    def __init__(self, app):
        QtGui.QDialog.__init__(self)
        self._app = app

        self._settings = QtCore.QSettings("Baseblack Ltd", "tk-nuke-templates")
        self.user = tank.util.get_shotgun_user(self._app.shotgun)  # used for filtering

        # set up the UI
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.name.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[A-Za-z0-9]+'), self))
        self.ui.tags.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp('[a-z0-9_, ]+'), self))

        # convienence cleanup method
        self._setupModelViews()

        # signals
        self.ui.show.currentIndexChanged.connect(self._showsChangeIndexCallback)
        self.ui.sequence.currentIndexChanged.connect(self._sequenceChangeIndexCallback)
        self.ui.publish.clicked.connect(self._publishCallback)

        # go live
        self.reloadShows()
        self.ui.show.setFocus()

    def _setupModelViews(self):
        self.shows_model = QtGui.QStandardItemModel()
        self.seq_model = QtGui.QStandardItemModel()
        self.shot_model = QtGui.QStandardItemModel()

        self.proxy_shows_model = ListProxyModel()
        self.proxy_seq_model = ListProxyModel()
        self.proxy_shot_model = ListProxyModel()

        self.proxy_shows_model.setSourceModel(self.shows_model)
        self.proxy_seq_model.setSourceModel(self.seq_model)
        self.proxy_shot_model.setSourceModel(self.shot_model)

        self.shows_view = QtGui.QListView()
        self.shows_view.setModel(self.proxy_shows_model)

        self.seq_view = QtGui.QListView()
        self.seq_view.setModel(self.proxy_seq_model)

        self.shot_view = QtGui.QListView()
        self.shot_view.setModel(self.proxy_shot_model)

        self.ui.show.setModel(self.proxy_shows_model)
        self.ui.show.setView(self.shows_view)

        self.ui.sequence.setModel(self.proxy_seq_model)
        self.ui.sequence.setView(self.seq_view)

        self.ui.shot.setModel(self.proxy_shot_model)
        self.ui.shot.setView(self.shot_view)

    def _loadShows(self, model):
        filters = [['sg_status','is','Active'],['tank_name','is_not', '']]
        fields = ['id',
                  'sg_code',
                  'tank_name',
                  'users']
        order = [{'field_name': 'project.Project.name', 'direction':'asc'}]
        sg_data = self._app.shotgun.find('Project', filters, fields, order)

        for show in sg_data:
            typeItem = QtGui.QStandardItem('Project')
            showItem = QtGui.QStandardItem(show.get('sg_code'))
            showItem.setData(show)
            usersItem = QtGui.QStandardItem(",".join([user.get('name') for user in show.get('users')]))

            model.appendRow([showItem, typeItem, usersItem])

    def _loadSequences(self, model, item):
        if hasattr(item, 'data'):
            filters = [['project.Project.sg_status', 'is', 'Active'],
                       ['sg_status_list', 'is_not', 'Omit'],
                       ['project.Project.id', 'is', item.data().get('id')]]
            fields = ['id',
                      'code',
                      'shots']
            order = [{'field_name': 'code', 'direction':'asc'}]
            sg_data = self._app.shotgun.find('Sequence', filters, fields, order)

            for sequence in sg_data:
                if not model.findItems(sequence.get('code')):
                    projectItem = QtGui.QStandardItem(item.data().get('sg_code'))
                    typeItem = QtGui.QStandardItem('Sequence')
                    seqItem = QtGui.QStandardItem(sequence.get('code'))
                    seqItem.setData(sequence)
                    model.appendRow([seqItem, typeItem, projectItem])

    def _loadShots(self, model, show, sequence):
        if hasattr(sequence, 'data'):
            for shot in sequence.data().get('shots'):
                if not shot.get('id') in [i.data().get('id') for i in model.findItems(shot.get('name'))]:
                    shotItem = QtGui.QStandardItem(shot.get('name'))
                    shotItem.setData(shot)
                    seqItem = QtGui.QStandardItem(sequence.data().get('code'))
                    seqItem.setData(shot)
                    projectItem = QtGui.QStandardItem(show.data().get('sg_code'))
                    model.appendRow([shotItem, projectItem, seqItem])

    def _setShowsFilter(self):
        self.proxy_shows_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_shows_model.setFilterFixedString(self.user.get('name'))
        self.proxy_shows_model.invalidateFilter()

    def _setSequenceFilter(self, pattern):
        self.proxy_seq_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_seq_model.setFilterFixedString(pattern)
        self.proxy_seq_model.invalidateFilter()

    def _setShotFilter(self, pattern):
        self.proxy_shot_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxy_shot_model.setFilterFixedString(pattern)
        self.proxy_shot_model.invalidateFilter()

    def reloadShows(self):
        self._setShowsFilter()
        self._loadShows(self.shows_model)
        self.reloadSequences()

    def reloadSequences(self):
        proxy_index = self.shows_view.currentIndex()
        source_index = self.proxy_shows_model.mapToSource(proxy_index)
        show_item = self.shows_model.itemFromIndex(source_index)

        if hasattr(show_item, 'data'):
            self._setSequenceFilter(show_item.data().get('sg_code'))
            self._loadSequences(self.seq_model, show_item)
            self.ui.sequence.setCurrentIndex(0)
            self.reloadShots()
        else:
            self._setSequenceFilter('None')
            self._setShotFilter('None')

    def reloadShots(self):
        source_index = self.proxy_shows_model.mapToSource(self.shows_view.currentIndex())
        show_item = self.shows_model.itemFromIndex(source_index)

        source_index = self.proxy_seq_model.mapToSource(self.seq_view.currentIndex())
        seq_item = self.seq_model.itemFromIndex(source_index)

        if hasattr(seq_item, 'data'):
            self._setShotFilter(seq_item.data().get('code'))
            self._loadShots(self.shot_model, show_item, seq_item)
            self.ui.shot.setCurrentIndex(0)
        else:
            self._setShotFilter('None')

    def _showsChangeIndexCallback(self, val):
        """
        Callback function.
        """
        self.reloadSequences()

    def _sequenceChangeIndexCallback(self, val):
        """
        Callback function.
        """
        self.reloadShots()

    def _publishCallback(self):
        """
        Fuck me. Its take ALL FUCKING DAY to get to this func.
        """

        # Early out if we've not set a name yet.
        if not self.ui.name.text():
            return nuke.message('Eeek! No name has been entered!')
        if not len(nuke.selectedNodes()):
            return nuke.message('Argh! No nodes have been selected!')

        # tough love for the model selection. we do this at the last minute so as
        # not to trigger the index changed signal, altering our other indices until
        # after we've finished processing the publish.
        source_index = self.proxy_shows_model.mapToSource(self.shows_view.currentIndex())
        if not source_index.isValid():
            proxy_index = self.proxy_shows_model.index(0,0)
            self.shows_view.setCurrentIndex(proxy_index)
            source_index = self.proxy_shows_model.mapToSource(self.shows_view.currentIndex())
        show = self.shows_model.itemFromIndex(source_index).data()

        source_index = self.proxy_seq_model.mapToSource(self.seq_view.currentIndex())
        sequence = self.seq_model.itemFromIndex(source_index).data() if source_index.isValid() else {}

        source_index = self.proxy_shot_model.mapToSource(self.shot_view.currentIndex())
        shot = self.shot_model.itemFromIndex(source_index).data() if source_index.isValid() else {}

        # Setup seed fields for tank_template resolution.
        fields = {}
        fields['name'] = self.ui.name.text()
        fields['Project'] = show.get('tank_name')
        fields['Show'] = show.get('sg_code')
        fields['Sequence'] = sequence.get('code')
        fields['Shot'] = shot.get('code')

        # Setup templates to use
        name_setting = self._app.get_setting('template_show_name')
        path_setting = self._app.get_setting('template_show_path')

        if fields['Shot']:
            name_setting = self._app.get_setting('template_shot_name')
            path_setting = self._app.get_setting('template_shot_path')
        elif fields['Sequence']:
            name_setting = self._app.get_setting('template_sequence_name')
            path_setting = self._app.get_setting('template_sequence_path')

        # Create a tank instance for the project we want to publish to.
        # Then retrieve the template objects from that instance.
        publish_tank = tank.tank_from_path('/mnt/shows/%s' % show.get('tank_name', ''))
        template_name = publish_tank.templates[name_setting]
        template_path = publish_tank.templates[path_setting]

        # Find existing publishes.
        previous_publishes = publish_tank.paths_from_template(template_path, fields, ['version'])
        fields['version'] = 1
        if previous_publishes:
            fields['version'] += template_path.get_fields(previous_publishes[-1])['version']

        # Setup data for publishing
        publish = {}
        publish['name'] = template_name.apply_fields(fields)
        publish['version'] = fields['version']
        publish['file_path'] = template_path.apply_fields(fields)
        publish['comment'] = self.ui.comments_text.toPlainText()
        publish['tags'] = self.ui.tags.text()
        publish['context'] = publish_tank.context_from_path(publish['file_path'])

        if not publish['comment'] or not publish['tags']:
            nuke.warning("Comments/tags for publish have been left blank, this will make it harder for others to use")

        # Do the file save and publish into Shotgun.
        try:
            publish_directory = os.path.dirname(publish['file_path'])
            if not os.path.exists(publish_directory):
                os.makedirs(publish_directory, 0775)
            nuke.nodeCopy(publish['file_path'])
        except OSError:
            return nuke.critical("Cannot create output path for saving nodes")
        except RuntimeError as err:
            self._app.log_debug(err)
            return nuke.critical("Cannot save out nodes to disk")

        if os.path.exists(publish['file_path']):
            result = tank.util.register_publish(publish_tank,
                                                publish['context'],
                                                publish['file_path'],
                                                publish['name'],
                                                publish['version'],
                                                comment = publish['comment'],
                                                tank_type = 'Nuke Script Template')
            if result:
                publish_tank.shotgun.update('TankPublishedFile', result['id'], {'sg_tags': publish['tags']})
                nuke.message('Template Published\n\nName: %s\n\nUse the explorer or Shotgun for details.' % publish['name'])
                self.close()
        else:
            nuke.critical("Cannot save out nodes to disk")

