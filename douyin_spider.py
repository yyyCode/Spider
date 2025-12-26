import re
import time
import os
import requests
from playwright.sync_api import sync_playwright

class DouyinSpider:
    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Referer": "https://www.douyin.com/"
        }
        self.video_url = None
        self.save_dir = "videos"  # 设置保存目录
        
        # 确保保存目录存在
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            print(f"已创建下载目录: {self.save_dir}")

    def handle_response(self, response):
        """
        监听网络响应，获取视频流地址
        """
        # 过滤出视频响应，通常包含 .mp4 或者 content-type 是 video
        if '.mp4' in response.url or 'video/mp4' in response.headers.get('content-type', ''):
            # 排除一些可能是广告或者封面的链接，尽量获取长链接
            if not self.video_url:
                print(f"发现视频流地址: {response.url[:60]}...")
                self.video_url = response.url

    def run(self):
        with sync_playwright() as p:
            # 启动浏览器，headless=True 表示无头模式（不显示浏览器界面），False 表示显示
            print("正在启动浏览器...")
            browser = p.chromium.launch(headless=True)
            
            # 创建上下文，设置 User-Agent 和 窗口大小
            context = browser.new_context(
                user_agent=self.headers["User-Agent"],
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()

            # 监听网络请求响应
            page.on("response", self.handle_response)

            print(f"正在访问: {self.url}")
            try:
                page.goto(self.url, timeout=60000) # 增加超时时间
                page.wait_for_load_state("networkidle") # 等待网络空闲
            except Exception as e:
                print(f"页面加载可能超时，继续尝试提取: {e}")

            # 获取页面标题作为文件名
            title = page.title()
            # 清理文件名非法字符
            title = re.sub(r'[\\/:*?"<>|]', '', title).strip()
            if not title or title == "抖音":
                # 尝试从页面内容获取更准确的描述
                try:
                    desc_element = page.query_selector('h1') or page.query_selector('.desc')
                    if desc_element:
                        title = desc_element.inner_text()
                        title = re.sub(r'[\\/:*?"<>|]', '', title).strip()
                except:
                    pass
            
            if not title:
                title = f"douyin_{int(time.time())}"
            
            # 截断过长的标题
            if len(title) > 50:
                title = title[:50]
                
            print(f"视频标题: {title}")

            # 如果监听网络请求没有获取到，尝试直接解析页面元素
            if not self.video_url:
                print("监听网络未获取到地址，尝试从页面元素解析...")
                try:
                    # 尝试查找 video 标签
                    video_element = page.query_selector('video')
                    if video_element:
                        src = video_element.get_attribute('src')
                        if src:
                            # 处理 blob: 开头的地址（这种通常无法直接下载，需要更复杂的流处理，这里简单处理 http 开头的）
                            if src.startswith('http'):
                                self.video_url = src
                            elif src.startswith('//'):
                                self.video_url = 'https:' + src
                except Exception as e:
                    print(f"元素解析出错: {e}")

            if self.video_url:
                print(f"最终视频地址: {self.video_url}")
                self.download_video(self.video_url, os.path.join(self.save_dir, f"{title}.mp4"))
            else:
                print("抱歉，未能提取到视频下载链接。可能是因为：")
                print("1. 视频需要登录才能观看")
                print("2. 遇到了验证码")
                print("3. 网络加载过慢")
                print("建议：尝试将 headless=False 改为 True 观察浏览器行为。")

            browser.close()

    def download_video(self, url, filepath):
        print(f"开始下载: {filepath}")
        try:
            # 抖音视频链接通常需要带上 headers 避免 403
            response = requests.get(url, headers=self.headers, stream=True)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            # 简单的进度显示
                            if total_size > 0:
                                percent = (downloaded_size / total_size) * 100
                                print(f"\r下载进度: {percent:.2f}%", end="")
                print(f"\n下载完成！文件已保存至: {filepath}")
            else:
                print(f"下载失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"下载出错: {e}")

def extract_url_from_text(text):
    """
    从混合文本中提取 URL
    """
    # 尝试匹配 http 或 https 开头的链接
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    if urls:
        return urls[0]
    return None

if __name__ == "__main__":
    print("="*50)
    print("抖音视频学习爬虫 (Playwright版)")
    print("注意：本脚本仅供学习交流，请勿用于非法用途")
    print("="*50)
    
    # 提示用户输入
    raw_input = input("请粘贴抖音分享文本 (包含链接即可): ")
    
    if raw_input:
        target_url = extract_url_from_text(raw_input)
        
        if target_url:
            print(f"识别到链接: {target_url}")
            spider = DouyinSpider(target_url)
            spider.run()
        else:
            print("未在输入中识别到有效的 http/https 链接")
    else:
        print("未输入内容，程序退出")
