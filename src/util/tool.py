import json
import os
import re
import time
import uuid

import hmac
from hashlib import sha256
from urllib.parse import quote

from bs4 import BeautifulSoup

from src.util import Log
from conf import config




class CTime(object):
    def __init__(self):
        self._t1 = time.time()

    def Refresh(self, clsName, des='', checkTime=100):
        t2 = time.time()
        diff = int((t2 - self._t1) * 1000)
        if diff >= checkTime:
            text = 'CTime2 consume:{} ms, {}.{}'.format(diff, clsName, des)
            Log.Warn(text)
            # 超过0.5秒超时写入数据库
        self._t1 = t2
        return diff


def time_me(fn):
    def _wrapper(*args, **kwargs):
        start = time.time()
        rt = fn(*args, **kwargs)
        diff = int((time.time() - start) * 1000)
        if diff >= 100:
            clsName = args[0]
            strLog = 'time_me consume,{} ms, {}.{}'.format(diff, clsName, fn.__name__)
            # Log.w(strLog)
            Log.Warn(strLog)
        return rt
    return _wrapper


class ToolUtil(object):
    @classmethod
    def GetHeader(cls, _url: str, method: str) -> dict:
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        return header

    @staticmethod
    def DictToUrl(paramDict):
        assert isinstance(paramDict, dict)
        data = ''
        for k, v in paramDict.items():
            data += quote(str(k)) + '=' + quote(str(v))
            data += '&'
        return data.strip('&')

    @staticmethod
    def ParseFromData(desc, src):
        try:
            if isinstance(src, str):
                src = json.loads(src)
            for k, v in src.items():
                setattr(desc, k, v)
        except Exception as es:
            Log.Error(es)

    @staticmethod
    def GetUrlHost(url):
        host = url.replace("https://", "")
        host = host.replace("http://", "")
        host = host.split("/")[0]
        return host

    @staticmethod
    def GetDateStr(createdTime):
        timeArray = time.strptime(createdTime, "%Y-%m-%dT%H:%M:%S.%f%z")
        tick = int(time.mktime(timeArray)-time.timezone)
        now = int(time.time())
        day = int((int(now - time.timezone) / 86400) - (int(tick - time.timezone) / 86400))
        return time.localtime(tick), day

    @staticmethod
    def GetDownloadSize(downloadLen):
        kb = downloadLen / 1024.0
        if kb <= 0.1:
            size = str(downloadLen) + "bytes"
        else:
            mb = kb / 1024.0
            if mb <= 0.1:
                size = str(round(kb, 2)) + "kb"
            else:
                size = str(round(mb, 2)) + "mb"
        return size

    @staticmethod
    def GetScaleAndNoise(w, h):
        dot = w * h
        # 条漫不放大
        if max(w, h) >= 2561:
            return 1, 3
        if dot >= 1920 * 1440:
            return 2, 3
        if dot >= 1920 * 1080:
            return 2, 3
        elif dot >= 720 * 1080:
            return 2, 3
        elif dot >= 240 * 720:
            return 2, 3
        else:
            return 2, 3

    @staticmethod
    def GetLookScaleModel(w, h, category):
        dot = w * h
        # 条漫不放大

        if max(w, h) >= 2561:
            return ToolUtil.GetModelByIndex(0)
        return ToolUtil.GetModelByIndex(ToolUtil.GetLookModel(category))

    @staticmethod
    def GetDownloadScaleModel(w, h):
        dot = w * h
        # 条漫不放大
        if not config.CanWaifu2x:
            return {}
        import waifu2x
        if max(w, h) >= 2561:
            return {"model": waifu2x.MODEL_ANIME_STYLE_ART_RGB_NOISE3, "scale": 1, "index": 0}
        return ToolUtil.GetModelByIndex(config.DownloadModel)

    @staticmethod
    def GetPictureFormat(data):
        if data[:8] == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a":
            return "png"
        elif data[:2] == b"\xff\xd8":
            return "jpg"
        return "jpg"

    @staticmethod
    def GetPictureSize(data):
        from PIL import Image
        from io import BytesIO
        a = BytesIO(data)
        img = Image.open(a)
        a.close()
        return img.width, img.height
        # picFormat = ToolUtil.GetPictureFormat(data)
        # weight, height = 1, 1
        # if picFormat == "png":
        #     # head = 8 + 4 + 4
        #     data2 = data[16:24]
        #     weight = int.from_bytes(data2[:4], byteorder='big', signed=False)
        #     height = int.from_bytes(data2[5:], byteorder='big', signed=False)
        # elif picFormat == "jpg":
        #     size = min(1000, len(data))
        #
        #     index = 0
        #     while index < size:
        #         if data[index] == 255:
        #             index += 1
        #             if 192 <= data[index] <= 206:
        #                 index += 4
        #                 if index + 4 >= size:
        #                     continue
        #                 height = int.from_bytes(data[index:index + 2], byteorder='big', signed=False)
        #                 weight = int.from_bytes(data[index + 2:index + 4], byteorder='big', signed=False)
        #                 break
        #             else:
        #                 continue
        #         index += 1
        # return weight, height

    @staticmethod
    def GetDataModel(data):
        picFormat = ToolUtil.GetPictureFormat(data)
        if picFormat == "png":
            IDATEnd = 8 + 25
            dataSize = int.from_bytes(data[IDATEnd:IDATEnd + 4], byteorder="big", signed=False)
            if dataSize >= 10:
                return ""
            dataType = data[IDATEnd + 4:IDATEnd + 8]
            if dataType == b"tEXt":
                return data[IDATEnd + 8:IDATEnd + 8 + dataSize].decode("utf-8")
            return ""
        elif picFormat == "jpg":
            if data[:4] != b"\xff\xd8\xff\xe0":
                return ""
            size = int.from_bytes(data[4:6], byteorder="big", signed=False)
            if size >= 100:
                return ""
            if data[4 + size:4 + size + 2] != b"\xff\xfe":
                return
            size2 = int.from_bytes(data[4 + size + 2:4 + size + 2 + 2], byteorder="big", signed=False) - 2
            if size2 >= 100:
                return
            return data[4 + size2 + 2 + 2:4 + size2 + 2 + 2 + size2].decode("utf-8")
        return ""

    @staticmethod
    def GetLookModel(category):
        if config.LookModel == 0:
            if "Cosplay" in category or "cosplay" in category or "CosPlay" in category or "COSPLAY" in category:
                return 2
            return 3
        else:
            return config.LookModel

    @staticmethod
    def GetDownloadModel():
        if config.DownloadModel == 0:
            return config.Model1
        return getattr(config, "Model"+str(config.DownloadModel), config.Model1)

    @staticmethod
    def GetModelAndScale(model):
        if not model:
            return 0, 1, 1
        model = model.get('index', 0)
        if model == 0:
            return 0, 3, 1
        elif model == 1:
            return 1, 3, 2
        elif model == 2:
            return 2, 3, 2
        elif model == 3:
            return 3, 3, 2
        return 0, 1, 1

    @staticmethod
    def GetModelByIndex(index):
        if not config.CanWaifu2x:
            return {}
        import waifu2x
        if index == 0:
            return {"model": waifu2x.MODEL_CUNET_NO_SCALE_NOISE3, "scale": 1, "index": index}
        elif index == 1:
            return {"model": waifu2x.MODEL_CUNET_NOISE3, "scale": 2, "index": index}
        elif index == 2:
            return {"model": waifu2x.MODEL_PHOTO_NOISE3, "scale": 2, "index": index}
        elif index == 3:
            return {"model": waifu2x.MODEL_ANIME_STYLE_ART_RGB_NOISE3, "scale": 2, "index": index}
        return {"model": waifu2x.MODEL_CUNET_NOISE3, "scale": 2, "index": index}

    @staticmethod
    def GetCanSaveName(name):
        return name.replace("/", "").replace("|", "").replace("*", "").\
            replace("\\", "").replace("?", "").replace(":", "").replace("*", "").\
            replace("<", "").replace(">", "").replace("\"", "").replace(" ", "")

    @staticmethod
    def LoadCachePicture(filePath):
        try:
            c = CTime()
            if not os.path.isfile(filePath):
                return None
            with open(filePath, "rb") as f:
                data = f.read()
                c.Refresh("LoadCache", filePath)
                return data
        except Exception as es:
            Log.Error(es)
        return None

    @staticmethod
    def ParseBookIndex(data):
        soup = BeautifulSoup(data, features="lxml")
        tag = soup.find("table", class_="itg gltc")
        bookInfos = []
        if not tag:
            return [], 1
        for tr in tag.children:
            from src.book.book import BookInfo
            info = BookInfo()
            baseInfo = info.baseInfo
            for td in tr.children:
                className = " ".join(td.attrs.get('class', []))
                if className == "gl1c glcat":
                    baseInfo.category = td.text
                elif className == "gl2c":
                    bookInfos.append(info)
                    picture = td.find("img")
                    baseInfo.title = picture.attrs.get("title")
                    url = picture.attrs.get("data-src")
                    if url:
                        baseInfo.imgUrl = url
                        baseInfo.imgData = picture.attrs.get("src")
                    else:
                        baseInfo.imgUrl = picture.attrs.get("src")

                    timeTag = td.find("div", id=re.compile(r"postedpop_\d+"))
                    baseInfo.id = re.findall(r"\d+", timeTag.attrs.get("id"))[0]
                    baseInfo.timeStr = timeTag.text
                elif className == "gl3c glname":
                    baseInfo.bookUrl = td.next.attrs.get("href")
                    for tag in td.find_all("div", class_="gt"):
                        baseInfo.tags.append(tag.attrs.get("title"))

                    pass
                elif className == "gl4c glhide":
                    pass

        table = soup.find("table", class_="ptt")
        maxPage = 1
        for td in table.tr.children:
            if getattr(td, "a", None):
                pages = td.a.text
                datas = re.findall(r"\d+", pages)
                if not datas:
                    continue
                maxPage = max(maxPage, int(datas[0]))
        return bookInfos, maxPage

    @staticmethod
    def ParseBookInfo(data):
        soup = BeautifulSoup(data, features="lxml")
        tag = soup.find("div", id="gdd")
        table = tag.find("table")
        from src.book.book import BookPageInfo
        info = BookPageInfo()
        for tr in table.find_all("tr"):
            key = tr.find("td", class_="gdt1").text.replace(":", "")
            value = tr.find("td", class_="gdt2").text
            info.kv[key] = value
        info.posted = info.kv.get("Posted")
        info.language = info.kv.get("Language")
        info.fileSize = info.kv.get("File Size")
        mo = re.search(r'\d+', info.kv.get("Length"))
        if mo:
            info.pages = int(mo.group())
        for tag in soup.find_all("div", class_="gdtm"):
            url = tag.a.attrs.get('href')
            index = int(tag.a.img.attrs.get('alt'))
            info.picUrl[index] = url
        table = soup.find("table", class_="ptt")
        maxPage = 1
        for td in table.tr.children:
            if getattr(td, "a", None):
                pages = td.a.text
                datas = re.findall(r"\d+", pages)
                if not datas:
                    continue
                maxPage = max(maxPage, int(datas[0]))

        comment = soup.find("div", id="cdiv")
        for tag in comment.find_all("div", class_="c1"):
            times = tag.find("div", class_="c3").text
            data = tag.find("div", class_="c6").text
            info.comment.append([times, data])
        return info, maxPage

    @staticmethod
    def ParsePictureInfo(data):
        soup = BeautifulSoup(data, features="lxml")
        tag = soup.find("div", id="i3")
        imgUrl = tag.a.img.attrs.get("src")
        mo = re.search("(?<=showkey)(\s*=\s*\")\w+", data)
        imgKey = mo.group().replace("\"", "").replace("=", "").replace(" ", "")
        return imgUrl, imgKey


    @staticmethod
    def ParsePictureInfo2(data):
        data = json.loads(data)
        tag = data.get('i3')
        mo = re.search("(?<=src=\")\S+\"", str(tag))
        if not mo:
            return ""
        imgUrl = mo.group().replace("\\/", "/").replace("\"", "")
        return imgUrl

    @staticmethod
    def MergeUrlParams(url, data: dict):
        if not data:
            return url
        if url[-1] != "/":
            url += "/?"
        for key, value in data.items():
            url += "{}={}".format(key, value)
            url += "&"
        return url.strip("&")
