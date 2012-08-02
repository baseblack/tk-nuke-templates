# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'search_dialog.ui'
#
# Created: Mon Jul 30 17:27:14 2012
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(888, 601)
        font = QtGui.QFont()
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setBold(False)
        Dialog.setFont(font)
        Dialog.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 9, 768, 30))
        self.label.setObjectName("label")
        self.left_view = TreeBrowserWidget(Dialog)
        self.left_view.setGeometry(QtCore.QRect(10, 61, 427, 503))
        self.left_view.setObjectName("tree")
        self.importButton = QtGui.QPushButton(Dialog)
        self.importButton.setGeometry(QtCore.QRect(762, 569, 115, 27))
        self.importButton.setObjectName("importButton")
        self.refresh = QtGui.QPushButton(Dialog)
        self.refresh.setGeometry(QtCore.QRect(9, 569, 115, 27))
        self.refresh.setMinimumSize(QtCore.QSize(115, 0))
        self.refresh.setObjectName("refresh")
        self.right_view = TemplateBrowserWidget(Dialog)
        self.right_view.setGeometry(QtCore.QRect(450, 61, 429, 503))
        self.right_view.setObjectName("right_view")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Tank Templates", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "<b><big>Which template would you like to use today?</big></b>", None, QtGui.QApplication.UnicodeUTF8))
        self.importButton.setText(QtGui.QApplication.translate("Dialog", "Import It...", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh.setText(QtGui.QApplication.translate("Dialog", "Refresh", None, QtGui.QApplication.UnicodeUTF8))

from ..template_browser import TemplateBrowserWidget
from ..tree_browser import TreeBrowserWidget
from . import resources_rc
