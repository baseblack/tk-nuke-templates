# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tree.ui'
#
# Created: Mon Jul 30 11:41:15 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Tree(object):
    def setupUi(self, Tree):
        Tree.setObjectName("Tree")
        Tree.resize(400, 800)
        self.verticalLayout = QtGui.QVBoxLayout(Tree)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.view = QtGui.QTreeView(Tree)
        self.view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.view.setIndentation(10)
        self.view.setAnimated(True)
        self.view.setExpandsOnDoubleClick(True)
        self.view.setObjectName("view")
        self.view.header().setVisible(True)
        self.verticalLayout.addWidget(self.view)

        self.retranslateUi(Tree)
        QtCore.QMetaObject.connectSlotsByName(Tree)

    def retranslateUi(self, Tree):
        Tree.setWindowTitle(QtGui.QApplication.translate("Tree", "Form", None, QtGui.QApplication.UnicodeUTF8))

