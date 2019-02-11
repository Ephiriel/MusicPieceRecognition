# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LoadingLibrary.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoadingLibrary(object):
    def setupUi(self, LoadingLibrary):
        LoadingLibrary.setObjectName("LoadingLibrary")
        LoadingLibrary.setWindowModality(QtCore.Qt.ApplicationModal)
        LoadingLibrary.resize(400, 58)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/database.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap("icons/database.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        LoadingLibrary.setWindowIcon(icon)
        LoadingLibrary.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(LoadingLibrary)
        self.verticalLayout.setObjectName("verticalLayout")
        self.library_loading_progress_bar = QtWidgets.QProgressBar(LoadingLibrary)
        self.library_loading_progress_bar.setProperty("value", 0)
        self.library_loading_progress_bar.setObjectName("library_loading_progress_bar")
        self.verticalLayout.addWidget(self.library_loading_progress_bar)
        self.library_loading_task_label = QtWidgets.QLabel(LoadingLibrary)
        self.library_loading_task_label.setObjectName("library_loading_task_label")
        self.verticalLayout.addWidget(self.library_loading_task_label)

        self.retranslateUi(LoadingLibrary)
        QtCore.QMetaObject.connectSlotsByName(LoadingLibrary)

    def retranslateUi(self, LoadingLibrary):
        _translate = QtCore.QCoreApplication.translate
        LoadingLibrary.setWindowTitle(_translate("LoadingLibrary", "Loading Database"))
        self.library_loading_task_label.setText(_translate("LoadingLibrary", "currentlyPerforming"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    LoadingLibrary = QtWidgets.QDialog()
    ui = Ui_LoadingLibrary()
    ui.setupUi(LoadingLibrary)
    LoadingLibrary.show()
    sys.exit(app.exec_())

