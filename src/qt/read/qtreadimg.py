import weakref
from PySide2 import QtWidgets
from PySide2.QtCore import Qt, QRectF, QPointF, QSizeF, QEvent, QSize, QMimeData
from PySide2.QtGui import QPixmap, QPainter, QColor, QImage
from PySide2.QtWidgets import QDesktopWidget, QMessageBox

from conf import config
from src.book.book import BookMgr
from src.qt.com.qtbubblelabel import QtBubbleLabel
from src.qt.com.qtloading import QtLoading
from src.qt.read.qtreadimg_frame import QtImgFrame
from src.qt.util.qttask import QtTask
from src.qt.struct.qt_define import QtFileData

from src.server import req
from src.util import ToolUtil, Log
from src.util.status import Status


class QtReadImg(QtWidgets.QWidget):
    def __init__(self, owner):
        super(self.__class__, self).__init__()
        self.owner = weakref.ref(owner)
        self.resize(800, 800)
        self.loadingForm = QtLoading(self)
        self.bookId = ""
        self.epsId = 0
        self.resetCnt = config.ResetCnt
        self.curIndex = 0

        self.pictureData = {}
        self.waitPicData = set()
        self.maxPic = 0

        self.curPreLoadIndex = 0
        self.maxPreLoad = config.PreLoading

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QtImgFrame(self)

        self.gridLayout.addWidget(self.frame)
        self.setMinimumSize(300, 300)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.ShowAndCloseTool)
        self.isStripModel = False

        self.closeFlag = self.__class__.__name__   # 防止切换时异步加载图片错位

        self.waifu2xIdToIndex = {}
        self.indexToWaifu2xId = {}
        self.waitWaifuPicData = set()

        self.category = []
        self.isInit = False

    @property
    def graphicsView(self):
        return self.frame.graphicsView

    @property
    def graphicsItem(self):
        return self.frame.graphicsItem

    @property
    def qtTool(self):
        return self.frame.qtTool

    def closeEvent(self, a0) -> None:
        self.ReturnPage()
        self.owner().bookInfoForm.show()
        self.Clear()
        a0.accept()

    def Clear(self):
        self.qtTool.UpdateText("")
        self.qtTool.UpdateProcessBar(None)
        self.bookId = ""
        self.epsId = 0
        self.maxPic = 0
        self.curIndex = 0
        self.frame.scaleCnt = 0
        self.pictureData.clear()
        self.waifu2xIdToIndex.clear()
        self.indexToWaifu2xId.clear()
        self.waitWaifuPicData.clear()
        self.waitPicData.clear()
        QtTask().CancelTasks(self.closeFlag)
        QtTask().CancelConver(self.closeFlag)

    def OpenPage(self, bookId, name):
        if not bookId:
            return
        self.Clear()
        # info = BookMgr().GetBook(bookId)
        # if info:
        #     self.category = info.tags[:]
        self.qtTool.checkBox.setChecked(config.IsOpenWaifu)
        self.qtTool.SetData(isInit=True)
        self.graphicsItem.setPixmap(QPixmap())
        self.qtTool.SetData()
        self.qtTool.show()
        self.bookId = bookId
        self.graphicsItem.setPos(0, 0)
        if not self.isInit:
            desktop = QDesktopWidget()
            self.resize(desktop.width()//4*3, desktop.height()-100)
            self.move(desktop.width()//8, 0)


        # historyInfo = self.owner().historyForm.GetHistory(bookId)
        # if historyInfo and historyInfo.epsId == epsId:
        #     self.curIndex = historyInfo.picIndex
        # else:
        #     self.AddHistory()
        # self.AddHistory()

        self.loadingForm.show()
        self.StartLoadPicUrl()
        self.setWindowTitle(name)
        self.show()
        if config.IsTips:
            config.IsTips = 0
            msg = QMessageBox()
            msg.setStyleSheet("QLabel{"
                                 "min-width: 300px;"
                                 "min-height: 300px; "
                                 "}")
            msg.setWindowTitle("操作提示")
            msg.setText("""
            操作提示：             
                下一页：
                    点击右下角区域
                    左滑图片
                    使用键盘→
                上一页：
                    点击左下角区域
                    右滑图片
                    使用键盘←
                打开菜单：
                    点击上方区域
                    点击右键
                退出：
                    使用键盘ESC
            """)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    def ReturnPage(self):
        self.AddHistory()
        self.owner().bookInfoForm.LoadHistory()
        return

    def CheckLoadPicture(self):
        i = 0
        for i in range(self.curIndex, self.curIndex + self.maxPreLoad):
            if i >= self.maxPic:
                continue

            bookInfo = BookMgr().GetBook(self.bookId)
            if i not in self.pictureData:
                # 防止重复请求
                if i not in self.waitPicData:
                    imgUrl = bookInfo.pageInfo.picRealUrl.get(i+1)
                    if imgUrl:
                        self.AddDownloadTask(i, imgUrl)
                    else:
                        self.GetPictureUrl(i)

            elif config.IsOpenWaifu and i not in self.waitWaifuPicData:
                if not self.pictureData[i].data:
                    continue
                if not self.pictureData[i].waifuData:
                    imgUrl = bookInfo.pageInfo.picRealUrl.get(i + 1)
                    self.AddCovertData(imgUrl, i)
        pass

    def StartLoadPicUrl(self):
        bookInfo = BookMgr().GetBook(self.bookId)
        self.maxPic = bookInfo.pageInfo.pages
        self.CheckLoadPicture()
        self.qtTool.InitSlider(self.maxPic)
        return

    def UpdateProcessBar(self, data, laveFileSize, backParam):
        info = self.pictureData.get(backParam)
        if not info:
            return
        if laveFileSize < 0:
            info.downloadSize = 0
        if info.size <= 0:
            info.size = laveFileSize
        info.downloadSize += len(data)
        if self.curIndex != backParam:
            return
        self.qtTool.UpdateProcessBar(info)

    def CompleteDownloadPic(self, data, st, index):
        self.loadingForm.close()
        p = self.pictureData.get(index)
        if not p:
            p = QtFileData()
            self.pictureData[index] = p
        bookInfo = BookMgr().GetBook(self.bookId)
        self.waitPicData.discard(index)
        if st != Status.Ok:
            p.state = p.DownloadReset
            self.AddDownloadTask(index, bookInfo.pageInfo.picRealUrl.get(index+1))
        else:
            p.SetData(data, self.category)
            # if config.IsOpenWaifu:
            #     self.AddCovertData(picInfo, index)
            if index == self.curIndex:
                self.ShowImg()
            return

    def ShowImg(self, isShowWaifu=True):
        p = self.pictureData.get(self.curIndex)

        if not p or (not p.data):
            self.qtTool.SetData(state=QtFileData.Downloading)
            self.graphicsItem.setPixmap(QPixmap())
            self.qtTool.modelBox.setEnabled(False)
            return
        self.qtTool.modelBox.setEnabled(True)
        assert isinstance(p, QtFileData)
        if not isShowWaifu:
            p2 = p.data
            self.qtTool.SetData(waifuSize=QSize(0, 0), waifuDataLen=0)
        elif p.waifuData:
            p2 = p.waifuData
            self.qtTool.SetData(waifuSize=p.waifuQSize, waifuDataLen=p.waifuDataSize,
                                waifuTick=p.waifuTick)
        else:
            p2 = p.data

        self.qtTool.SetData(pSize=p.qSize, dataLen=p.size, state=p.state, waifuState=p.waifuState)
        self.qtTool.UpdateText(p.model)

        self.frame.pixMap = QPixmap()
        if config.IsLoadingPicture:
            self.frame.pixMap.loadFromData(p2)
        self.graphicsItem.setPixmap(self.frame.pixMap)
        self.graphicsView.setSceneRect(QRectF(QPointF(0, 0), QPointF(self.frame.pixMap.width(), self.frame.pixMap.height())))
        self.frame.ScalePicture()
        self.CheckLoadPicture()
        return True

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.KeyPress:
            return True
        else:
            return super(self.__class__, self).eventFilter(obj, ev)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
        else:
            if event.angleDelta().y() > 0:
                # self.zoomIn()
                point = self.graphicsItem.pos()
                self.graphicsItem.setPos(point.x(), point.y()+100)
            else:
                # self.zoomOut()
                point = self.graphicsItem.pos()
                self.graphicsItem.setPos(point.x(), point.y()-100)

    def zoomIn(self):
        """放大"""
        self.zoom(1.1)

    def zoomOut(self):
        """缩小"""
        self.zoom(1/1.1)

    def zoom(self, factor):
        """缩放
        :param factor: 缩放的比例因子
        """
        _factor = self.graphicsView.transform().scale(
            factor, factor).mapRect(QRectF(0, 0, 1, 1)).width()
        if _factor < 0.07 or _factor > 100:
            # 防止过大过小
            return
        if factor >= 1:
            if self.frame.scaleCnt >= 10:
                QtBubbleLabel.ShowMsgEx(self, "已经最大")
                return
            self.frame.scaleCnt += 1
        else:
            if self.frame.scaleCnt <= -10:
                QtBubbleLabel.ShowMsgEx(self, "已经最小")
                return
            self.frame.scaleCnt -= 1
        self.graphicsView.scale(factor, factor)

    def keyReleaseEvent(self, ev):
        if ev.modifiers() == Qt.ShiftModifier and ev.key() == Qt.Key_Left:
            self.qtTool.OpenLastEps()
            return
        if ev.modifiers() == Qt.ShiftModifier and ev.key() == Qt.Key_Right:
            self.qtTool.OpenNextEps()
            return
        if ev.key() == Qt.Key_Left:
            self.qtTool.LastPage()
            return
        elif ev.key() == Qt.Key_Right:
            self.qtTool.NextPage()
            return
        elif ev.key() == Qt.Key_Escape:
            self.qtTool.ReturnPage()
            return
        elif ev.key() == Qt.Key_Up:
            point = self.graphicsItem.pos()
            self.graphicsItem.setPos(point.x(), point.y()+50)
            return
        elif ev.key() == Qt.Key_Down:
            point = self.graphicsItem.pos()
            self.graphicsItem.setPos(point.x(), point.y()-50)
            return
        super(self.__class__, self).keyReleaseEvent(ev)

    def AddHistory(self):
        # TODO
        return
        bookName = self.owner().bookInfoForm.bookName
        url = self.owner().bookInfoForm.url
        path = self.owner().bookInfoForm.path
        self.owner().historyForm.AddHistory(self.bookId, bookName, self.epsId, self.curIndex, url, path)
        return

    def ShowAndCloseTool(self):
        if self.qtTool.isHidden():
            self.qtTool.show()
        else:
            self.qtTool.hide()

    def Waifu2xBack(self, data, waifu2xId, index, tick):
        self.waitWaifuPicData.discard(index)
        if waifu2xId > 0:
            self.waifu2xIdToIndex[waifu2xId] = index
            self.indexToWaifu2xId[index] = waifu2xId
        if waifu2xId not in self.waifu2xIdToIndex:
            Log.Error("Not found waifu2xId ：{}, index: {}".format(str(waifu2xId), str(index)))
            return
        p = self.pictureData.get(index)
        p.SetWaifuData(data, round(tick, 2))
        if index == self.curIndex:
            self.ShowImg()

    def AddCovertData(self, imgUrl, i):
        info = self.pictureData[i]
        if not info and info.data:
            return
        assert isinstance(info, QtFileData)
        # path = self.owner().downloadForm.GetConvertFilePath(self.bookId, self.epsId, i)
        QtTask().AddConvertTask(imgUrl+str(info.model.get('model', 0)), info.data, info.model, self.Waifu2xBack, i, self.closeFlag)
        self.waitWaifuPicData.add(i)

    def AddDownloadTask(self, i, imgUrl):
        # path = self.owner().downloadForm.GetDonwloadFilePath(self.bookId, self.epsId, i)
        QtTask().AddDownloadTask(imgUrl, "",
                                 downloadCallBack=self.UpdateProcessBar,
                                 completeCallBack=self.CompleteDownloadPic, backParam=i,
                                 isSaveCache=True, cleanFlag=self.closeFlag, filePath="")
        self.waitPicData.add(i)
        if i not in self.pictureData:
            data = QtFileData()
            self.pictureData[i] = data

    def GetPictureUrl(self, i):
        QtTask().AddHttpTask(req.GetBookImgUrl2(self.bookId, i+1), self.GetPictureUrlBack, i)
        self.waitPicData.add(i)

    def GetPictureUrlBack(self, msg, i):
        self.waitPicData.discard(i)
        self.CheckLoadPicture()
