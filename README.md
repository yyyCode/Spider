# 抖音视频学习爬虫 (Douyin Video Spider)

这是一个基于 Python 和 Playwright 的抖音视频下载工具，仅供学习和研究使用。

## 功能特点

- **自动嗅探**：利用 Playwright 监听网络请求，自动获取无水印（通常情况）视频流地址。
- **智能识别**：支持直接粘贴抖音分享的混合文本（包含中文、表情、链接等），自动提取链接。
- **自动保存**：视频自动下载并保存到项目根目录下的 `videos` 文件夹。
- **自动命名**：尝试获取视频标题作为文件名。

## 环境要求

- Python 3.8+
- Playwright

## 安装步骤

1. 克隆或下载本项目。
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 安装 Playwright 浏览器驱动：
   ```bash
   playwright install chromium
   ```

## 使用方法

1. 运行爬虫脚本：
   ```bash
   python douyin_spider.py
   ```
2. 在手机抖音 App 中找到想下载的视频，点击“分享” -> “复制链接”。
3. 将复制的内容（包含文字和链接）直接粘贴到终端并回车。
4. 视频将自动下载到 `videos/` 目录下。

## 注意事项

- 本项目仅供学习 Python 爬虫技术使用，请勿用于批量抓取、商业用途或侵犯他人版权。
- 爬虫可能因抖音页面更新或反爬策略调整而失效。

## 许可证

MIT License
