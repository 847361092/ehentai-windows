# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'bookinfo.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_BookInfo(object):
    def setupUi(self, BookInfo):
        if not BookInfo.objectName():
            BookInfo.setObjectName(u"BookInfo")
        BookInfo.resize(999, 808)
        self.gridLayout_2 = QGridLayout(BookInfo)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.stackedWidget = QStackedWidget(BookInfo)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.gridLayout_4 = QGridLayout(self.page)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.picture = QLabel(self.page)
        self.picture.setObjectName(u"picture")
        self.picture.setMinimumSize(QSize(240, 320))

        self.horizontalLayout.addWidget(self.picture)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.page)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(40, 16777215))

        self.horizontalLayout_3.addWidget(self.label)

        self.title = QLabel(self.page)
        self.title.setObjectName(u"title")

        self.horizontalLayout_3.addWidget(self.title)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_6 = QLabel(self.page)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMaximumSize(QSize(40, 20))

        self.horizontalLayout_8.addWidget(self.label_6)

        self.likes = QLabel(self.page)
        self.likes.setObjectName(u"likes")
        self.likes.setMaximumSize(QSize(16777215, 20))

        self.horizontalLayout_8.addWidget(self.likes)


        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_7 = QLabel(self.page)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMaximumSize(QSize(40, 20))

        self.horizontalLayout_9.addWidget(self.label_7)

        self.views = QLabel(self.page)
        self.views.setObjectName(u"views")
        self.views.setMaximumSize(QSize(16777215, 20))

        self.horizontalLayout_9.addWidget(self.views)


        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.updateTick = QLabel(self.page)
        self.updateTick.setObjectName(u"updateTick")
        self.updateTick.setEnabled(True)
        self.updateTick.setMinimumSize(QSize(80, 0))
        self.updateTick.setMaximumSize(QSize(80, 20))

        self.horizontalLayout_2.addWidget(self.updateTick)

        self.isFinished = QLabel(self.page)
        self.isFinished.setObjectName(u"isFinished")
        self.isFinished.setMinimumSize(QSize(80, 0))
        self.isFinished.setMaximumSize(QSize(80, 20))
        self.isFinished.setTextFormat(Qt.AutoText)
        self.isFinished.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.isFinished)

        self.startRead = QPushButton(self.page)
        self.startRead.setObjectName(u"startRead")
        self.startRead.setMaximumSize(QSize(16777215, 20))

        self.horizontalLayout_2.addWidget(self.startRead)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.horizontalLayout.addLayout(self.verticalLayout_2)


        self.gridLayout_3.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_3)

        self.tabWidget = QTabWidget(self.page)
        self.tabWidget.setObjectName(u"tabWidget")
        self.epsWidget = QWidget()
        self.epsWidget.setObjectName(u"epsWidget")
        self.epsLayout = QGridLayout(self.epsWidget)
        self.epsLayout.setObjectName(u"epsLayout")
        self.tabWidget.addTab(self.epsWidget, "")
        self.commentWidget = QWidget()
        self.commentWidget.setObjectName(u"commentWidget")
        self.commentLayout = QGridLayout(self.commentWidget)
        self.commentLayout.setObjectName(u"commentLayout")
        self.tabWidget.addTab(self.commentWidget, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.gridLayout_4.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page)

        self.gridLayout_2.addWidget(self.stackedWidget, 0, 0, 1, 1)


        self.retranslateUi(BookInfo)
        self.startRead.clicked.connect(BookInfo.StartRead)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(BookInfo)
    # setupUi

    def retranslateUi(self, BookInfo):
        BookInfo.setWindowTitle(QCoreApplication.translate("BookInfo", u"Form", None))
        self.picture.setText(QCoreApplication.translate("BookInfo", u"TextLabel", None))
        self.label.setText(QCoreApplication.translate("BookInfo", u"\u6807\u9898\uff1a", None))
        self.title.setText(QCoreApplication.translate("BookInfo", u"\u6807\u9898", None))
        self.label_6.setText(QCoreApplication.translate("BookInfo", u"\u9875\u6570:", None))
        self.likes.setText(QCoreApplication.translate("BookInfo", u"\u7231\u5fc3\u6570", None))
        self.label_7.setText(QCoreApplication.translate("BookInfo", u"\u6536\u85cf\u6570", None))
        self.views.setText(QCoreApplication.translate("BookInfo", u"\u6536\u85cf\u6570", None))
        self.updateTick.setText(QCoreApplication.translate("BookInfo", u"TextLabel", None))
        self.isFinished.setText(QCoreApplication.translate("BookInfo", u"\u5b8c\u672c", None))
        self.startRead.setText(QCoreApplication.translate("BookInfo", u"\u5f00\u59cb\u9605\u8bfb", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.epsWidget), QCoreApplication.translate("BookInfo", u"Tags", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.commentWidget), QCoreApplication.translate("BookInfo", u"\u8bc4\u8bba", None))
    # retranslateUi

