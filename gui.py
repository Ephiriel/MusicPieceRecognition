# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUI.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1073, 642)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/music.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_6.addWidget(self.label_2)
        self.database_item_list_widget = QtWidgets.QListWidget(self.centralwidget)
        self.database_item_list_widget.setMinimumSize(QtCore.QSize(200, 0))
        self.database_item_list_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.database_item_list_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.database_item_list_widget.setModelColumn(0)
        self.database_item_list_widget.setSelectionRectVisible(True)
        self.database_item_list_widget.setObjectName("database_item_list_widget")
        self.verticalLayout_6.addWidget(self.database_item_list_widget, 0, QtCore.Qt.AlignLeft)
        self.horizontalLayout_4.addLayout(self.verticalLayout_6)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.query_name_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.query_name_label.setFont(font)
        self.query_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.query_name_label.setObjectName("query_name_label")
        self.horizontalLayout_3.addWidget(self.query_name_label)
        self.verticalLayout_10.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.open_query_button = QtWidgets.QToolButton(self.centralwidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.open_query_button.setIcon(icon1)
        self.open_query_button.setObjectName("open_query_button")
        self.horizontalLayout_2.addWidget(self.open_query_button)
        self.save_query_button = QtWidgets.QToolButton(self.centralwidget)
        self.save_query_button.setIcon(icon)
        self.save_query_button.setObjectName("save_query_button")
        self.horizontalLayout_2.addWidget(self.save_query_button)
        self.play_query_button = QtWidgets.QToolButton(self.centralwidget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/play-record.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.play_query_button.setIcon(icon2)
        self.play_query_button.setObjectName("play_query_button")
        self.horizontalLayout_2.addWidget(self.play_query_button)
        self.record_query_button = QtWidgets.QToolButton(self.centralwidget)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("icons/record.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.record_query_button.setIcon(icon3)
        self.record_query_button.setObjectName("record_query_button")
        self.horizontalLayout_2.addWidget(self.record_query_button)
        self.search_query_button = QtWidgets.QToolButton(self.centralwidget)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("icons/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.search_query_button.setIcon(icon4)
        self.search_query_button.setObjectName("search_query_button")
        self.horizontalLayout_2.addWidget(self.search_query_button)
        self.verticalLayout_10.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_6.addLayout(self.verticalLayout_10)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setTextFormat(QtCore.Qt.AutoText)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_7.addWidget(self.label_3, 0, QtCore.Qt.AlignLeft)
        self.currently_playing_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.currently_playing_label.setFont(font)
        self.currently_playing_label.setText("")
        self.currently_playing_label.setObjectName("currently_playing_label")
        self.horizontalLayout_7.addWidget(self.currently_playing_label)
        self.verticalLayout_12.addLayout(self.horizontalLayout_7)
        self.music_position_slider = QtWidgets.QSlider(self.centralwidget)
        self.music_position_slider.setMaximumSize(QtCore.QSize(16777215, 10))
        self.music_position_slider.setStyleSheet("QSlider::groove:horizontal {\n"
"border: 1px solid #bbb;\n"
"background: white;\n"
"height: 4px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,\n"
"    stop: 0 #55f, stop: 1 #55f);\n"
"background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,\n"
"    stop: 0 #55f, stop: 1 #55f);\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #fff;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #eee, stop:1 #ccc);\n"
"border: 1px solid #777;\n"
"width: 10px;\n"
"margin-top: -2px;\n"
"margin-bottom: -2px;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:hover {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #fff, stop:1 #ddd);\n"
"border: 1px solid #444;\n"
"border-radius: 2px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal:disabled {\n"
"background: #bbb;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal:disabled {\n"
"background: #eee;\n"
"border-color: #999;\n"
"}\n"
"\n"
"QSlider::handle:horizontal:disabled {\n"
"background: #eee;\n"
"border: 1px solid #aaa;\n"
"border-radius: 4px;\n"
"}")
        self.music_position_slider.setOrientation(QtCore.Qt.Horizontal)
        self.music_position_slider.setObjectName("music_position_slider")
        self.verticalLayout_12.addWidget(self.music_position_slider)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem3)
        self.stop_button = QtWidgets.QToolButton(self.centralwidget)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap("icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stop_button.setIcon(icon5)
        self.stop_button.setObjectName("stop_button")
        self.horizontalLayout_8.addWidget(self.stop_button)
        self.play_pause_button = QtWidgets.QToolButton(self.centralwidget)
        self.play_pause_button.setIcon(icon)
        self.play_pause_button.setObjectName("play_pause_button")
        self.horizontalLayout_8.addWidget(self.play_pause_button)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem4)
        self.verticalLayout_12.addLayout(self.horizontalLayout_8)
        self.verticalLayout_11.addLayout(self.verticalLayout_12)
        self.verticalLayout.addLayout(self.verticalLayout_11)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label, 0, QtCore.Qt.AlignTop)
        self.result_table = QtWidgets.QTableWidget(self.centralwidget)
        self.result_table.setEnabled(True)
        self.result_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.result_table.setDragDropOverwriteMode(False)
        self.result_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.result_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.result_table.setShowGrid(False)
        self.result_table.setWordWrap(False)
        self.result_table.setCornerButtonEnabled(False)
        self.result_table.setObjectName("result_table")
        self.result_table.setColumnCount(3)
        self.result_table.setRowCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setItem(1, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setItem(2, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setItem(2, 2, item)
        self.result_table.horizontalHeader().setCascadingSectionResizes(False)
        self.result_table.horizontalHeader().setDefaultSectionSize(54)
        self.result_table.horizontalHeader().setHighlightSections(False)
        self.result_table.horizontalHeader().setMinimumSectionSize(20)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.verticalHeader().setVisible(False)
        self.verticalLayout_5.addWidget(self.result_table, 0, QtCore.Qt.AlignRight)
        self.query_result_list_widget = QtWidgets.QListWidget(self.centralwidget)
        self.query_result_list_widget.setMinimumSize(QtCore.QSize(200, 0))
        self.query_result_list_widget.setObjectName("query_result_list_widget")
        self.verticalLayout_5.addWidget(self.query_result_list_widget, 0, QtCore.Qt.AlignRight|QtCore.Qt.AlignTop)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.midiViewer = PianoWidget(self.centralwidget)
        self.midiViewer.setObjectName("midiViewer")
        self.verticalLayout_3.addWidget(self.midiViewer, 0, QtCore.Qt.AlignVCenter)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1073, 21))
        self.menubar.setObjectName("menubar")
        self.menuData = QtWidgets.QMenu(self.menubar)
        self.menuData.setObjectName("menuData")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad_Database = QtWidgets.QAction(MainWindow)
        self.actionLoad_Database.setIcon(icon1)
        self.actionLoad_Database.setObjectName("actionLoad_Database")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.action_save_query = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("ui/save-as.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_save_query.setIcon(icon6)
        self.action_save_query.setObjectName("action_save_query")
        self.action_load_query = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap("ui/music.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_load_query.setIcon(icon7)
        self.action_load_query.setObjectName("action_load_query")
        self.action_load_database = QtWidgets.QAction(MainWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap("ui/database.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_load_database.setIcon(icon8)
        self.action_load_database.setObjectName("action_load_database")
        self.action_open_database = QtWidgets.QAction(MainWindow)
        self.action_open_database.setIcon(icon8)
        self.action_open_database.setObjectName("action_open_database")
        self.action_open_query = QtWidgets.QAction(MainWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap("ui/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_open_query.setIcon(icon9)
        self.action_open_query.setObjectName("action_open_query")
        self.menuData.addAction(self.action_open_database)
        self.menuData.addSeparator()
        self.menuData.addAction(self.action_open_query)
        self.menuData.addAction(self.action_save_query)
        self.menuData.addSeparator()
        self.menuData.addAction(self.actionExit)
        self.menubar.addAction(self.menuData.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Melody Query Tool"))
        self.label_2.setText(_translate("MainWindow", "Database items"))
        self.query_name_label.setText(_translate("MainWindow", "Please select a query"))
        self.open_query_button.setToolTip(_translate("MainWindow", "Open a query"))
        self.open_query_button.setText(_translate("MainWindow", "..."))
        self.save_query_button.setToolTip(_translate("MainWindow", "Save a recorded query"))
        self.save_query_button.setText(_translate("MainWindow", "..."))
        self.play_query_button.setText(_translate("MainWindow", "..."))
        self.record_query_button.setToolTip(_translate("MainWindow", "record a new query"))
        self.record_query_button.setText(_translate("MainWindow", "..."))
        self.search_query_button.setToolTip(_translate("MainWindow", "Start a search for the selected query"))
        self.search_query_button.setText(_translate("MainWindow", "..."))
        self.label_3.setText(_translate("MainWindow", "Currently Playing:"))
        self.stop_button.setText(_translate("MainWindow", "..."))
        self.play_pause_button.setText(_translate("MainWindow", "..."))
        self.label.setText(_translate("MainWindow", "Query results"))
        item = self.result_table.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "Neue Zeile"))
        item = self.result_table.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "Neue Zeile"))
        item = self.result_table.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "Neue Zeile"))
        item = self.result_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Rank"))
        item = self.result_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Match at"))
        item = self.result_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Music Piece"))
        __sortingEnabled = self.result_table.isSortingEnabled()
        self.result_table.setSortingEnabled(False)
        item = self.result_table.item(0, 0)
        item.setText(_translate("MainWindow", "sdfa"))
        item = self.result_table.item(1, 0)
        item.setText(_translate("MainWindow", "af"))
        item = self.result_table.item(1, 2)
        item.setText(_translate("MainWindow", "sdf"))
        item = self.result_table.item(2, 1)
        item.setText(_translate("MainWindow", "asdf"))
        item = self.result_table.item(2, 2)
        item.setText(_translate("MainWindow", "sdfa"))
        self.result_table.setSortingEnabled(__sortingEnabled)
        self.menuData.setTitle(_translate("MainWindow", "File"))
        self.actionLoad_Database.setText(_translate("MainWindow", "Load Database"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.action_save_query.setText(_translate("MainWindow", "Save Query..."))
        self.action_load_query.setText(_translate("MainWindow", "Query"))
        self.action_load_database.setText(_translate("MainWindow", "Database"))
        self.action_open_database.setText(_translate("MainWindow", "Open Database..."))
        self.action_open_query.setText(_translate("MainWindow", "Open Query..."))

from piano_roll_editor import PianoWidget

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

