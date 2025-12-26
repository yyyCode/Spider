import os
import sys

# 【关键设置】
# 必须在导入 playwright 或其他模块之前设置

# 1. 确定潜在的浏览器路径
potential_paths = []

# (A) 单文件模式临时解压目录 (sys._MEIPASS)
if hasattr(sys, '_MEIPASS'):
    potential_paths.append(os.path.join(sys._MEIPASS, "ms-playwright"))
    
# (B) EXE 同级目录 (onedir 模式或外部依赖)
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
        potential_paths.append(os.path.join(base_dir, "ms-playwright"))
        potential_paths.append(os.path.join(base_dir, "_internal", "ms-playwright")) # PyInstaller >= 6.0 _internal 目录
        potential_paths.append(os.path.join(base_dir, "browsers")) # 兼容旧逻辑
        potential_paths.append(os.path.join(base_dir, "_internal", "browsers"))
    
# (C) 开发环境 (dist/browsers 或 dist/ms-playwright)
potential_paths.append(os.path.join(os.getcwd(), "dist", "ms-playwright"))
potential_paths.append(os.path.join(os.getcwd(), "ms-playwright"))

found_path = None
for p in potential_paths:
    if os.path.exists(p) and os.path.isdir(p) and os.listdir(p):
        # 简单检查里面有没有 chromium 文件夹
        if any("chromium" in name for name in os.listdir(p)):
            found_path = p
            break

if found_path:
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = found_path
    print(f"[环境配置] 使用本地浏览器依赖: {found_path}")
else:
    # 没找到就让它自己去下，或者使用系统默认
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
    print("[环境配置] 未检测到内嵌浏览器，将使用系统默认或在线下载")

import customtkinter as ctk
import threading
import subprocess
import multiprocessing
import traceback

from douyin_spider import DouyinSpider, extract_url_from_text

# 设置主题
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("抖音视频下载器")
        self.geometry("700x500")

        # 布局配置
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. 顶部输入区域
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.url_label = ctk.CTkLabel(self.input_frame, text="粘贴分享口令或链接:")
        self.url_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.url_entry = ctk.CTkEntry(self.input_frame, placeholder_text="例如: 2.30 h@o.qe... https://v.douyin.com/...")
        self.url_entry.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")

        self.download_btn = ctk.CTkButton(self.input_frame, text="开始下载", command=self.start_download_thread)
        self.download_btn.grid(row=1, column=1, padx=10, pady=(5, 10))

        # 1.5 路径选择区域
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.path_frame.grid_columnconfigure(1, weight=1)

        self.path_label = ctk.CTkLabel(self.path_frame, text="保存路径:")
        self.path_label.grid(row=0, column=0, padx=10, pady=10)

        # 默认保存路径为当前目录下的 videos
        default_path = os.path.join(os.getcwd(), "videos")
        self.path_entry = ctk.CTkEntry(self.path_frame, placeholder_text="选择保存路径")
        self.path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.path_entry.insert(0, default_path)

        self.browse_btn = ctk.CTkButton(self.path_frame, text="浏览...", width=60, command=self.browse_directory)
        self.browse_btn.grid(row=0, column=2, padx=10, pady=10)

        # 2. 环境检查区域
        self.status_label = ctk.CTkLabel(self, text="系统就绪", text_color="gray")
        self.status_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")

        # 3. 日志输出区域
        self.log_textbox = ctk.CTkTextbox(self, width=600, height=300)
        self.log_textbox.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.log_textbox.configure(state="disabled")

        # 启动时检查环境
        self.after(500, self.check_environment)

    def browse_directory(self):
        """选择文件夹"""
        from tkinter import filedialog
        directory = filedialog.askdirectory(initialdir=self.path_entry.get())
        if directory:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, directory)


    def log(self, message):
        """线程安全的日志输出"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")
        print(message)

    def check_environment(self):
        """检查 Playwright 环境"""
        threading.Thread(target=self._check_env_thread, daemon=True).start()

    def _check_env_thread(self):
        self.log("正在检查运行环境...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                try:
                    # 打印一下预期路径，方便调试
                    # 注意：launch 之前可能无法获取具体的 executable_path，除非指定了 channel
                    # 这里尝试直接启动，捕获错误
                    self.log(f"浏览器安装路径模式: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH')}")
                    
                    # 尝试启动浏览器来验证驱动是否安装
                    # 显式指定 chromium
                    browser = p.chromium.launch(headless=True)
                    browser.close()
                    self.log("环境检查通过：Chromium 驱动已安装。")
                    self.status_label.configure(text="环境正常", text_color="green")
                except Exception as e:
                    self.log(f"检测到驱动异常: {e}")
                    self.log("正在尝试自动安装 Playwright 浏览器驱动 (这可能需要几分钟)...")
                    self.status_label.configure(text="正在安装依赖组件...", text_color="orange")
                    self.install_playwright()
        except Exception as e:
            self.log(f"环境严重错误: {e}")
            self.log(traceback.format_exc())

    def install_playwright(self):
        """调用命令安装 playwright"""
        try:
            # 简单方式：尝试直接运行命令
            # 使用 "playwright install" 而不是 "install chromium"，确保依赖完整
            cmd = [sys.executable, "-m", "playwright", "install"]

            self.log(f"执行安装命令: {' '.join(cmd)}")
            
            # 显式传递环境变量，确保子进程也使用正确的路径配置
            env = os.environ.copy()
            # 移除强制指定 "0"，让其继承当前进程的 PLAYWRIGHT_BROWSERS_PATH 配置
            # env["PLAYWRIGHT_BROWSERS_PATH"] = "0"

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env, # 传递环境变量
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            # 读取输出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(f"[安装进度] {output.strip()}")
            
            # 读取错误输出（如果有）
            stderr_output = process.stderr.read()
            if stderr_output:
                self.log(f"[安装日志] {stderr_output.strip()}")

            rc = process.poll()
            if rc == 0:
                self.log("组件安装成功！请重新点击下载尝试。")
                self.status_label.configure(text="环境已修复", text_color="green")
            else:
                self.log(f"组件安装失败，返回码: {rc}")
                self.status_label.configure(text="环境安装失败", text_color="red")
        except Exception as e:
            self.log(f"执行安装命令出错: {e}")
            self.log(traceback.format_exc())

    def start_download_thread(self):
        raw_input = self.url_entry.get()
        if not raw_input:
            self.log("错误: 请先输入内容")
            return
            
        save_dir = self.path_entry.get()
        if not save_dir:
            self.log("错误: 请选择保存路径")
            return

        self.download_btn.configure(state="disabled", text="下载中...")
        threading.Thread(target=self.run_spider, args=(raw_input, save_dir), daemon=True).start()

    def run_spider(self, raw_input, save_dir):
        try:
            url = extract_url_from_text(raw_input)
            if not url:
                self.log("错误: 未能在输入中识别到有效的链接")
                return

            self.log(f"开始处理链接: {url}")
            self.log(f"保存目录: {save_dir}")
            # 传递 headless=True 确保后台静默运行
            spider = DouyinSpider(url, headless=True, log_callback=self.log)
            # 临时修改：由于 douyin_spider.py 的 __init__ 方法并没有接收 save_dir 参数（它是在内部写死或硬编码的，或者之前的修改漏掉了？）
            # 让我们检查一下 douyin_spider.py 的定义。如果不通过参数传递，需要手动设置属性。
            spider.save_dir = save_dir
            spider.run()
        except Exception as e:
            self.log(f"运行出错: {e}")
        finally:
            # 恢复按钮状态（需要使用 after 在主线程更新 UI）
            self.after(0, lambda: self.download_btn.configure(state="normal", text="开始下载"))

if __name__ == "__main__":
    # Windows 下 PyInstaller 打包多进程应用必须调用此函数
    # 防止进程递归创建导致弹出多个窗口
    multiprocessing.freeze_support()
    
    # 【关键修复】
    # 拦截子进程调用。当程序尝试通过 subprocess 调用自身来执行命令时（例如安装 playwright），
    # sys.argv 会包含参数。我们需要拦截这些调用，执行相应逻辑，而不是启动 GUI。
    if len(sys.argv) > 1:
        # 检查是否是 -m playwright 调用
        if sys.argv[1] == "-m" and len(sys.argv) > 2 and sys.argv[2] == "playwright":
            # 重置 sys.argv，使其看起来像直接运行 playwright 模块
            # 原始参数: [exe_path, "-m", "playwright", "install", ...]
            # 目标参数: ["playwright", "install", ...]
            sys.argv = sys.argv[2:]
            try:
                from playwright.__main__ import main
                sys.exit(main())
            except ImportError:
                print("Error: Could not import playwright.__main__")
                sys.exit(1)
            except SystemExit as e:
                # 捕获 playwright main 的退出
                sys.exit(e.code)
    
    app = App()
    app.mainloop()
