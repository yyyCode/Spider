from douyin_spider import DouyinSpider, extract_url_from_text
import sys

def main():
    print("="*60)
    print("抖音视频爬虫命令行版 v1.0")
    print("功能：自动过滤广告，下载高清无水印(尽可能)视频")
    print("操作：粘贴分享口令或链接，按回车开始下载。输入 'q' 退出。")
    print("="*60)

    while True:
        try:
            # 使用 sys.stdout.flush() 确保提示符立即显示
            print("\n请输入分享口令或链接: ", end="", flush=True)
            raw_input = sys.stdin.readline().strip()
            
            if not raw_input:
                continue
                
            if raw_input.lower() in ['q', 'quit', 'exit']:
                print("程序已退出。")
                break
            
            url = extract_url_from_text(raw_input)
            if not url:
                print("错误: 未识别到有效链接，请重新输入。")
                continue
                
            print(f"正在启动爬虫抓取: {url}")
            # 实例化爬虫并运行
            spider = DouyinSpider(url)
            spider.run()
            print("----------------------------------------")
            
        except KeyboardInterrupt:
            print("\n程序已退出")
            break
        except Exception as e:
            print(f"发生未预期的错误: {e}")

if __name__ == "__main__":
    main()
