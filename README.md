# Douyin Video Downloader (抖音视频下载器)

一个基于 Python Playwright 和 CustomTkinter 的抖音视频下载工具。

## ✨ 功能特点

*   **GUI 图形界面**：简洁美观的界面，操作简单。
*   **自动提取链接**：支持直接粘贴包含中文、表情符号的混合分享文本，自动提取 URL。
*   **高清无水印**：自动嗅探并下载高清无水印视频。
*   **离线运行**：提供打包好的 EXE 版本，内嵌所有浏览器依赖，无需安装 Python 或配置环境即可运行。
*   **智能防检测**：内置 stealth 脚本和动态行为模拟，有效规避反爬检测。

## 📥 下载地址

请前往本仓库的 [Releases 页面](https://github.com/yyyCode/spider/releases) 下载最新版本的 `DouyinDownloader.zip`。

> **注意**：下载后解压，直接运行文件夹内的 `DouyinDownloader.exe` 即可。首次运行无需联网下载组件。

## 🛠️ 本地开发与运行

如果你想自己修改代码或从源码运行：

### 1. 克隆仓库
```bash
git clone https://github.com/yyyCode/spider.git
cd spider
```

### 2. 安装依赖
确保已安装 Python 3.8+，然后运行：
```bash
pip install -r requirements.txt
```

### 3. 安装浏览器驱动
```bash
playwright install chromium
```

### 4. 运行
**方式一：运行 GUI**
```bash
python gui_app.py
```
或者直接运行启动脚本（自动检查依赖）：
```powershell
./Start-Spider.ps1
```

**方式二：命令行模式**
```bash
python cli.py "你的分享链接"
```

## 📦 如何打包

如果你修改了代码并想重新打包 EXE：

1. 确保安装了 `pyinstaller`：
   ```bash
   pip install pyinstaller
   ```

2. 运行打包命令（包含所有依赖）：
   ```bash
   pyinstaller --noconfirm --onedir --windowed --name "DouyinDownloader" --icon "NONE" --hidden-import "playwright" --add-data "stealth.min.js;." --add-data "C:\Users\86178\AppData\Local\ms-playwright\chromium-1200;ms-playwright/chromium-1200" --add-data "C:\Users\86178\AppData\Local\ms-playwright\ffmpeg-1011;ms-playwright/ffmpeg-1011" --add-data "C:\Users\86178\AppData\Local\ms-playwright\chromium_headless_shell-1200;ms-playwright/chromium_headless_shell-1200" gui_app.py
   ```
   *(注意：上述命令中的路径可能需要根据你的实际 Playwright 安装位置进行调整)*

## 📝 License

MIT
