import json
import weakref

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import QRect, Qt, QSize, QEvent
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QListWidget, QListWidgetItem, QLabel, QApplication, QHBoxLayout, QLineEdit, QPushButton, \
    QVBoxLayout

from conf import config
from src.book.book import BookMgr
from src.qt.com.qtbubblelabel import QtBubbleLabel
from src.qt.com.qtimg import QtImgMgr
from src.qt.com.qtlistwidget import QtBookList, QtCategoryList
from src.qt.com.qtloading import QtLoading
from src.server import req, Log, Server, ToolUtil, QtTask
from src.util.status import Status
from ui.bookinfo import Ui_BookInfo


class QtBookInfo(QtWidgets.QWidget, Ui_BookInfo):
    def __init__(self, owner):
        super(self.__class__, self).__init__()
        Ui_BookInfo.__init__(self)
        self.setupUi(self)
        self.owner = weakref.ref(owner)
        self.loadingForm = QtLoading(self)
        self.bookId = ""
        self.url = ""
        self.path = ""
        self.bookName = ""
        self.lastEpsId = -1
        self.pictureData = None

        self.msgForm = QtBubbleLabel(self)
        self.picture.installEventFilter(self)
        self.title.setGeometry(QRect(328, 240, 329, 27 * 4))
        self.title.setWordWrap(True)
        self.title.setAlignment(Qt.AlignTop)
        self.title.setContextMenuPolicy(Qt.CustomContextMenu)
        self.title.customContextMenuRequested.connect(self.CopyTitle)

        self.epsListWidget = QListWidget(self)
        # self.epsListWidget.setFlow(self.epsListWidget.LeftToRight)
        self.epsListWidget.setWrapping(True)
        self.epsListWidget.setFrameShape(self.epsListWidget.NoFrame)
        self.epsListWidget.setResizeMode(self.epsListWidget.Adjust)

        self.epsLayout.addWidget(self.epsListWidget)

        self.listWidget = QtBookList(self, self.__class__.__name__, owner)
        self.listWidget.InitUser(self.LoadNextPage)

        self.commentLayout.addWidget(self.listWidget)
        layout = QHBoxLayout()
        self.commentLine = QLineEdit()
        layout.addWidget(self.commentLine)
        self.commentButton = QPushButton("发送评论")
        layout.addWidget(self.commentButton)
        self.commentLayout.addLayout(layout, 1, 0)
        self.commentButton.clicked.connect(self.SendComment)
        self.commentButton.setEnabled(False)

        # self.stackedWidget.addWidget(self.qtReadImg)
        # self.epsListWidget.clicked.connect(self.OpenReadImg)

        self.closeFlag = self.__class__.__name__ + "-close"         # 切换book时，取消加载
        # self.title.setTextInteractionFlags(Qt.TextSelectableByMouse)
        # self.description.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.tags = self.owner().tags

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.stackedWidget.currentIndex() == 1:
            self.stackedWidget.setCurrentIndex(0)
            self.owner().qtReadImg.AddHistory()
            self.LoadHistory()
            a0.ignore()
        else:
            a0.accept()

    def CopyTitle(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.title.text())
        self.msgForm.ShowMsg("复制标题")
        return

    # def OpenAutor(self):
    #     text = self.autor.text()
    #     self.owner().userForm.listWidget.setCurrentRow(0)
    #     self.owner().searchForm.searchEdit.setText(text)
    #     self.owner().searchForm.Search()
    #     return

    def Clear(self):
        self.stackedWidget.setCurrentIndex(0)
        QtTask().CancelTasks(self.closeFlag)
        self.epsListWidget.clear()
        self.listWidget.clear()

    def OpenBook(self, bookId):
        self.bookId = bookId
        self.setWindowTitle(self.bookId)
        self.setFocus()
        # if self.bookId in self.owner().downloadForm.downloadDict:
        #     self.download.setEnabled(False)
        # else:
        #     self.download.setEnabled(True)

        self.Clear()
        self.show()
        self.loadingForm.show()
        QtTask().AddHttpTask(req.BookInfoReq(bookId), self.OpenBookBack)

    def close(self):
        super(self.__class__, self).close()

    def OpenBookBack(self, maxPages):
        self.loadingForm.close()
        self.listWidget.UpdatePage(1, maxPages)
        self.listWidget.UpdateState()
        self.epsListWidget.clear()
        info = BookMgr().GetBook(self.bookId)
        self.title.setText(info.baseInfo.title)
        self.bookName = info.baseInfo.title
        self.picture.setText("图片加载中...")
        self.url = info.baseInfo.imgUrl
        self.path = ""
        self.updateTick.setText(info.pageInfo.posted)
        self.views.setText(str(info.pageInfo.favorites))
        self.likes.setText(str(info.pageInfo.pages))
        for tag in info.baseInfo.tags:
            label = QLabel(tag)
            label.setContentsMargins(20, 10, 20, 10)
            label.setWordWrap(True)
            item = QListWidgetItem(self.epsListWidget)
            item.setBackground(QColor(0, 0, 0, 0))
            item.setSizeHint(label.sizeHint() + QSize(2, 0))

            tagData = tag.split(":")
            if len(tagData) >= 2:
                if tagData[0] in self.tags:
                    if tagData[1] in self.tags[tagData[0]].get("data"):
                        tagInfo = self.tags[tagData[0]].get("data").get(tagData[1], {})
                        label.setText(self.tags[tagData[0]].get("name", "") + ":" + tagInfo.get("dest", ""))
                        item.setToolTip(tagInfo.get('description', ""))

            # item.setToolTip(epsInfo.title)
            self.epsListWidget.setItemWidget(item, label)

        if config.IsLoadingPicture:
            QtTask().AddDownloadTask(self.url, "", completeCallBack=self.UpdatePicture, cleanFlag=self.closeFlag)
        self.GetCommnetBack(info.pageInfo.comment)
        return

    def UpdatePicture(self, data, status):
        if status == Status.Ok:
            self.pictureData = data
            pic = QtGui.QPixmap()
            pic.loadFromData(data)
            pic.scaled(self.picture.size(), QtCore.Qt.KeepAspectRatio)
            self.picture.setPixmap(pic)
            # self.picture.setScaledContents(True)
            self.update()
        else:
            self.picture.setText("图片加载失败")
        return

    # 加载评论
    def GetCommnetBack(self, data):
        try:
            self.listWidget.page = 1
            self.listWidget.pages = 1
            self.tabWidget.setTabText(1, "评论({})".format(str(len(data))))
            for index, v in enumerate(data):
                createdTime, content = v
                self.listWidget.AddUserItem("", 0, 0, content, "", createdTime, index+1, "",
                                            "", "", "", 0)
            return
        except Exception as es:
            Log.Error(es)

    # def AddDownload(self):
    #     self.owner().epsInfoForm.OpenEpsInfo(self.bookId)
        # if self.owner().downloadForm.AddDownload(self.bookId):
        #     QtBubbleLabel.ShowMsgEx(self, "添加下载成功")
        # else:
        #     QtBubbleLabel.ShowMsgEx(self, "已在下载列表")
        # self.download.setEnabled(False)

    # def AddFavority(self):
    #     User().AddAndDelFavorites(self.bookId)
    #     QtBubbleLabel.ShowMsgEx(self, "添加收藏成功")
    #     self.favorites.setEnabled(False)

    def LoadNextPage(self):
        return
        # self.loadingForm.show()
        # QtTask().AddHttpTask(
        #     lambda x: Server().Send(req.GetComments(self.bookId, self.listWidget.page + 1), bakParam=x),
        #     self.GetCommnetBack, cleanFlag=self.closeFlag)
        # return

    def StartRead(self):
        # if self.lastEpsId >= 0:
        #     self.OpenReadIndex(self.lastEpsId)
        # else:
        # self.OpenReadIndex(0)
        self.hide()
        self.owner().qtReadImg.OpenPage(self.bookId, self.title.text())
        return

    def LoadHistory(self):
        return

    def ClickTagsItem(self, item):
        text = item.text()
        self.owner().userForm.listWidget.setCurrentRow(1)
        self.owner().searchForm.searchEdit.setText(text)
        self.owner().searchForm.Search()
        return

    def SendComment(self):
        return
        # data = self.commentLine.text()
        # if not data:
        #     return
        # self.commentLine.setText("")
        # self.loadingForm.show()
        # QtTask().AddHttpTask(lambda x: Server().Send(req.SendComment(self.bookId, data), bakParam=x), callBack=self.SendCommentBack)

    # def SendCommentBack(self, msg):
    #     try:
    #         data = json.loads(msg)
    #         if data.get("code") == 200:
    #             QtTask().AddHttpTask(lambda x: Server().Send(req.GetComments(self.bookId), bakParam=x),
    #                                             self.GetCommnetBack, cleanFlag=self.closeFlag)
    #         else:
    #             self.loadingForm.close()
    #             QtBubbleLabel.ShowErrorEx(self, data.get("message", "错误"))
    #         self.commentLine.setText("")
    #     except Exception as es:
    #         self.loadingForm.close()
    #         Log.Error(es)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                if self.pictureData:
                    QtImgMgr().ShowImg(self.pictureData)
                return True
            else:
                return False
        else:
            return super(self.__class__, self).eventFilter(obj, event)

    def keyPressEvent(self, ev):
        key = ev.key()
        if Qt.Key_Escape == key:
            self.close()
        return super(self.__class__, self).keyPressEvent(ev)
