# [picacg-windows](https://github.com/tonquer/picacg-windows) | ehentai-windows
- E站window客户端（现已支持Linux和macOS），界面使用QT。
- 该项目仅供技术研究使用，请勿用于其他用途。
- 如果觉得本项目对你有所帮助，请点个star关注，感谢支持

## waifu2x功能
- waifu2x是用来提高图片分辨率和去噪点的功能， 介绍 "https://github.com/nagadomi/waifu2x"
- waifu2x-python，修改了waifu2x-ncnn-vulkan部分功能
- waifu2x功能使用的是 "https://github.com/tonquer/waifu2x-ncnn-vulkan-python" 改进而来，打包成lib目录下的waifu2x.pyd。

## 如何使用
  ### Windows (测试使用win10)
  1. 下载最新的版本 https://github.com/tonquer/picacg-windows/releases
  2. 解压zip
  3. 打开start.exe
  4. 后续有更新，只需要下载最新版本覆盖原目录即可
  5. 如果无法初始化waifu2x，请更新显卡驱动，安装 [Vs运行库](https://download.visualstudio.microsoft.com/download/pr/366c0fb9-fe05-4b58-949a-5bc36e50e370/015EDD4E5D36E053B23A01ADB77A2B12444D3FB6ECCEFE23E3A8CD6388616A16/VC_redist.x64.exe)，如果还是无法启用，说明你的电脑不支持vulkan。
  ### macOS (测试使用 macOS 10.15.7)
  1. 下载最新的版本 https://github.com/tonquer/picacg-windows/releases
  2. 解压 7z
  3. 将解压出的 PicACG 拖入访达 (Finder) 左侧侧栏的应用程序 (Applications) 文件夹中
  4. 从启动台 (Launchpad) 中找到并打开 PicACG
  #### 对于 M1 Mac 用户
  * 作者没有 Arm Mac, 所以没有办法提供已经打包好的应用程序
  * 如果您拥有 M1 Mac, 可以尝试参考下面的过程手动运行或者进行打包
  ### Linux (测试使用deepin 20.2)
  1. 下载qt依赖， http://ftp.br.debian.org/debian/pool/main/x/xcb-util/libxcb-util1_0.4.0-1+b1_amd64.deb
  2. 安装依赖，sudo dpkg -i ./libxcb-util1_0.4.0-1+b1_amd64.deb
  3. 下载最新的版本 https://github.com/tonquer/picacg-windows/releases
  4. 解压tar -zxvf bika.tar.gz 
  5. cd bika && chmod +x start
  6. ./start
  7. 要想使用waifu2x请确定你的设备支持vulkan，然后安装vulkan驱动包，sudo apt install mesa-vulkan-drivers

## 如何编译
1. git clone https://github.com/tonquer/picacg-windows.git
2. 安装 Python 3.7+ (Mac 用户则只需要安装 [Xcode 12.4 及其命令行工具 (官方)](https://developer.apple.com/download/more/?name=Xcode%2012.4) ,安装后自带双架构 Python 3.8.2, 下载时需登录 iCloud 账号
3. pip install -r requirements.tzt
4. 可以使用 pyinstaller -F -w start.py 打包成 exe
### 对于 macOS 用户
````bash
pyinstaller --clean --log-level TRACE --onedir --name PicACG \
            --add-binary waifu2x.so:. --hidden-import PySide2 --hidden-import requests \
            --hidden-import urllib3 --hidden-import websocket-client --hidden-import pillow \
            --hidden-import conf --hidden-import resources --hidden-import src \
            --hidden-import src.index --hidden-import src.qt --hidden-import src.qt.chat \
            --hidden-import src.qt.com --hidden-import src.qt.download \
            --hidden-import src.qt.main --hidden-import src.qt.menu \
            --hidden-import src.qt.read --hidden-import src.qt.struct \
            --hidden-import src.qt.user --hidden-import src.qt.util --hidden-import src.server \
            --hidden-import src.user --hidden-import src.util --hidden-import ui \
            --strip --windowed -i Icon.icns \
            start.py
cp -avf data example models resources dist/PicACG.app/Contents/MacOS
````
* 打包完成以后可以在 dist 目录下找到应用程序 (.app)

## 感谢以下项目
- https://github.com/nagadomi/waifu2x
- https://github.com/nihui/waifu2x-ncnn-vulkan
- https://github.com/webmproject/libwebp
- https://github.com/Tencent/ncnn
- 如有任何问题，欢迎提ISSUE
