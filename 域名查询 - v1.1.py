import urllib.request
import urllib.parse
import re
import time
import random
import csv
import signal
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import os
import sys
import colorama

# 初始化colorama以支持Windows命令行的彩色输出
colorama.init()

# 定义颜色
class Colors:
    HEADER = '\033[95m'      # 紫色
    BLUE = '\033[94m'        # 蓝色
    CYAN = '\033[96m'        # 青色
    GREEN = '\033[92m'       # 绿色
    YELLOW = '\033[93m'      # 黄色
    RED = '\033[91m'         # 红色
    ENDC = '\033[0m'         # 重置颜色
    BOLD = '\033[1m'         # 加粗
    UNDERLINE = '\033[4m'    # 下划线

def print_header(text):
    """打印带格式的标题"""
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")

def print_info(text):
    """打印普通信息"""
    print(f"{Colors.BLUE}{text}{Colors.ENDC}")

def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}{text}{Colors.ENDC}")

def print_warning(text):
    """打印警告信息"""
    print(f"{Colors.YELLOW}{text}{Colors.ENDC}")

def print_error(text):
    """打印错误信息"""
    print(f"{Colors.RED}{text}{Colors.ENDC}")

def print_domain(text):
    """打印域名信息"""
    print(f"{Colors.CYAN}{text}{Colors.ENDC}")

def print_highlight(text):
    """打印高亮信息"""
    print(f"{Colors.BOLD}{text}{Colors.ENDC}")

def print_progress(current, total, domain):
    """打印进度信息"""
    percentage = (current / total) * 100
    print(f"{Colors.BOLD}[{current}/{total}]{Colors.ENDC} {Colors.CYAN}({percentage:.1f}%){Colors.ENDC} 查询: {Colors.YELLOW}{domain}{Colors.ENDC}")

# 全局变量，用于保存结果和处理信号
global_results = []
global_output_file = "bing_index_results.csv"
is_interrupted = False

def save_current_results(results=None, output_file=None):
    """保存当前已有的结果到CSV文件"""
    if results is None:
        results = global_results
    
    if output_file is None:
        output_file = global_output_file
        
    if not results:
        print_warning("没有需要保存的结果")
        return

    # 按收录页面数量排序
    results.sort(key=lambda x: x['indexed_pages'], reverse=True)
    
    # 创建自动保存的文件名（如果未指定）
    if output_file == "bing_index_results.csv":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        auto_save_file = f"bing_autosave_{timestamp}.csv"
    else:
        # 为指定的文件名添加自动保存前缀
        file_name, file_ext = os.path.splitext(output_file)
        auto_save_file = f"{file_name}_autosave{file_ext}"
    
    fieldnames = ["domain", "status", "indexed_pages", "checked_time"]
    
    # 添加BOM标记以确保Excel正确识别UTF-8编码
    with open(auto_save_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print_warning(f"已自动保存 {len(results)} 条结果到文件: {auto_save_file}")

def signal_handler(sig, frame):
    """处理键盘中断和终止信号"""
    global is_interrupted
    is_interrupted = True
    print_warning("\n检测到程序中断信号！正在保存已查询数据...")
    save_current_results()
    print_warning("数据已保存，程序即将退出...")
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
if hasattr(signal, 'SIGBREAK'):  # Windows Ctrl+Break
    signal.signal(signal.SIGBREAK, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)  # 终止信号

class BingIndexChecker:
    def __init__(self, delay_range=(3, 7), debug=False):
        """
        初始化Bing收录查询器（使用Python基础库，无外部依赖）
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.bing.com/'
        }
        self.debug = debug
        self.delay_range = delay_range
        
    def check_domain(self, domain):
        """
        查询单个域名在Bing的收录情况
        """
        # 检查是否被中断
        global is_interrupted
        if is_interrupted:
            return None
            
        # 保存原始域名
        original_domain = domain
        
        # 确保域名格式正确
        if domain.startswith('http://') or domain.startswith('https://'):
            # 提取域名部分
            parsed_url = urllib.parse.urlparse(domain)
            domain_for_query = parsed_url.netloc
            if parsed_url.path and parsed_url.path != '/':
                domain_for_query += parsed_url.path
        else:
            # 没有协议，直接使用
            domain_for_query = domain
            
        # 构建查询URL (使用site:语法)
        query = f"site:{domain_for_query}"
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.bing.com/search?q={encoded_query}"
        
        try:
            # 打印查询信息
            print_info(f"  查询参数: site:{domain_for_query}")
            print_info(f"  查询URL: {search_url}")
            
            # 创建请求
            req = urllib.request.Request(search_url, headers=self.headers)
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=15) as response:
                html_content = response.read().decode('utf-8')
                
            # 调试模式下保存HTML
            if self.debug:
                debug_file = f"debug_{domain_for_query.replace('/', '_')}.html"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print_info(f"  已将响应保存到: {debug_file}")
            
            print_highlight("  开始分析HTML元素...")
            
            # 提取页面标题
            title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
            if title_match:
                page_title = title_match.group(1)
                print_info(f"  页面标题: {page_title}")
            
            # 检查是否没有结果
            no_results_match = re.search(r'<li\s+class="b_no".*?>(.*?)</li>', html_content, re.DOTALL)
            if no_results_match:
                no_results_text = no_results_match.group(1)
                print_warning(f"  检测到未收录元素: <li class=\"b_no\">...")
                no_results_text_clean = re.sub(r'<.*?>', ' ', no_results_text)
                print_warning(f"  内容: '{no_results_text_clean[:60]}...'")
                if "没有与此相关的结果" in no_results_text:
                    return None
            
            # 查找结果计数
            count_match = re.search(r'<span\s+class="sb_count">(.*?)</span>', html_content)
            if count_match:
                count_text = count_match.group(1)
                print_success(f"  检测到收录元素: <span class=\"sb_count\">{count_text}</span>")
                # 提取数字
                number_match = re.search(r'(\d[\d,]*)', count_text)
                if number_match:
                    count_str = number_match.group(1)
                    count = int(count_str.replace(',', ''))
                    return {
                        "domain": original_domain,
                        "status": "已收录",
                        "indexed_pages": count,
                        "checked_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
            
            # 检查是否有搜索结果列表
            algo_results = re.findall(r'<li\s+class="b_algo"', html_content)
            if algo_results:
                result_count = len(algo_results)
                print_success(f"  检测到搜索结果: 找到 {result_count} 个 <li class=\"b_algo\"> 元素")
                return {
                    "domain": original_domain,
                    "status": "已收录(无法获取确切数量)",
                    "indexed_pages": result_count,
                    "checked_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # 未找到收录信息
            print_warning("  未检测到任何收录相关元素，判定为未收录")
            return None
            
        except Exception as e:
            if self.debug:
                print_error(f"  请求异常: {str(e)}")
            return None
    
    def batch_check(self, domains, output_file="bing_index_results.csv"):
        """
        批量查询多个域名并保存结果到CSV文件
        """
        global global_results, global_output_file
        global_output_file = output_file
        results = []
        global_results = results  # 更新全局结果列表
        
        total = len(domains)
        
        print_header(f"开始查询 {total} 个域名的收录情况...")
        print("")
        
        try:
            for i, domain in enumerate(domains, 1):
                # 检查是否被中断
                global is_interrupted
                if is_interrupted:
                    break
                    
                # 进度显示
                print_progress(i, total, domain)
                
                # 查询域名
                result = self.check_domain(domain)
                
                # 只记录有收录的域名
                if result is not None:
                    results.append(result)
                    global_results = results  # 更新全局结果
                    
                    # 打印结果
                    print_success(f"  状态: {result['status']}, 收录页面: {result['indexed_pages']}")
                else:
                    print_warning(f"  状态: 未收录，不记录到结果文件")
                
                # 每10个域名自动保存一次（或自定义其他数量）
                if len(results) > 0 and len(results) % 10 == 0:
                    auto_save_file = f"bing_autosave_temp.csv"
                    self._save_to_csv(results, auto_save_file)
                    print_info(f"  自动保存点: 已保存 {len(results)} 条结果到临时文件")
                
                # 添加随机延迟
                if i < total:
                    delay = random.uniform(self.delay_range[0], self.delay_range[1])
                    print_info(f"  等待 {delay:.2f} 秒...")
                    print("")  # 空行分隔
                    time.sleep(delay)
            
            # 如果有收录的域名，保存最终结果
            if results:
                # 按收录页面数量排序
                results.sort(key=lambda x: x['indexed_pages'], reverse=True)
                
                # 保存结果到CSV文件
                self._save_to_csv(results, output_file)
                
                print("")
                print_success(f"查询完成! 共找到 {len(results)} 个已收录域名，结果已保存到 {output_file}")
            else:
                print("")
                print_warning(f"查询完成! 未找到任何已收录域名")
                
            return results
            
        except KeyboardInterrupt:
            # 键盘中断时保存已有结果
            print_warning("\n检测到用户中断！正在保存已查询数据...")
            if results:
                self._save_to_csv(results, f"{output_file}_interrupted.csv")
                print_warning(f"已保存 {len(results)} 条结果到文件: {output_file}_interrupted.csv")
            raise
            
        except Exception as e:
            # 其他异常时也保存结果
            print_error(f"\n程序出错: {str(e)}")
            if results:
                self._save_to_csv(results, f"{output_file}_error.csv")
                print_warning(f"已保存 {len(results)} 条结果到文件: {output_file}_error.csv")
            raise
    
    def _save_to_csv(self, results, filename):
        """
        将结果保存到CSV文件
        """
        fieldnames = ["domain", "status", "indexed_pages", "checked_time"]
        
        # 添加BOM标记以确保Excel正确识别UTF-8编码
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)


def select_file():
    """
    打开文件选择对话框
    """
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title='选择包含域名列表的文本文件',
        filetypes=[('文本文件', '*.txt'), ('所有文件', '*.*')]
    )
    
    root.destroy()
    
    return file_path if file_path else None

def select_save_file():
    """
    打开文件保存对话框
    """
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.asksaveasfilename(
        title='选择保存结果的位置',
        defaultextension='.csv',
        filetypes=[('CSV文件', '*.csv'), ('所有文件', '*.*')],
        initialfile='bing_index_results.csv'
    )
    
    root.destroy()
    
    return file_path if file_path else 'bing_index_results.csv'

def display_banner():
    """显示程序横幅"""
    banner = """
╔═════════════════════════════════════════════════════╗
║                                                     ║
║  ██████╗ ██╗███╗   ██╗ ██████╗                      ║
║  ██╔══██╗██║████╗  ██║██╔════╝                      ║
║  ██████╔╝██║██╔██╗ ██║██║  ███╗                     ║
║  ██╔══██╗██║██║╚██╗██║██║   ██║                     ║
║  ██████╔╝██║██║ ╚████║╚██████╔╝                     ║
║  ╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝                      ║
║                                                     ║
║  bing收录查询工具 v1.1                              ║
║  本软件由AI编写，作者博客:blog.xiaoxinbk.cn         ║
║                                                     ║
╚═════════════════════════════════════════════════════╝
    """
    print(f"{Colors.CYAN}{banner}{Colors.ENDC}")

def main():
    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')
    
    display_banner()
    print_header("Bing网站收录批量查询工具 - 小新博客")
    print_header("======================================")
    print("")
    
    # 显示版权信息
    print_info("版权信息: 本软件由 AI编写，作者博客：blog.xiaoxinbk.cn")
    print_success("【新功能】程序中断时会自动保存已查询数据")
    print("")
    
    print_info("请选择包含域名列表的文本文件...")
    input_file = select_file()
    if not input_file:
        print_error("未选择任何文件，程序退出")
        return
        
    print_info("请选择保存结果的位置...")
    output_file = select_save_file()
    global global_output_file
    global_output_file = output_file
        
    # 读取域名文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            domains = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print_error(f"读取文件错误: {str(e)}")
        input(f"{Colors.YELLOW}按Enter键退出...{Colors.ENDC}")
        return
    
    if not domains:
        print_error("错误: 未找到任何域名")
        input(f"{Colors.YELLOW}按Enter键退出...{Colors.ENDC}")
        return
    
    debug_mode = False
    print_info("是否启用调试模式(保存HTML响应)? (y/n): [默认:n]")
    choice = input().lower()
    if choice == 'y' or choice == 'yes':
        debug_mode = True
        print_success("已启用调试模式")
    else:
        print_info("未启用调试模式")
    
    min_delay = 3.0
    max_delay = 7.0
    print_info(f"请输入查询延迟范围(秒)，默认为 {min_delay}-{max_delay}，格式如 3-7: ")
    try:
        delay_input = input()
        if delay_input and '-' in delay_input:
            min_str, max_str = delay_input.split('-')
            min_delay = float(min_str.strip())
            max_delay = float(max_str.strip())
            print_success(f"设置查询延迟范围为: {min_delay}-{max_delay}秒")
        else:
            print_info(f"使用默认延迟范围: {min_delay}-{max_delay}秒")
    except:
        print_warning(f"输入格式错误，使用默认延迟范围: {min_delay}-{max_delay}秒")
    
    print("")
    print_success(f"已加载 {len(domains)} 个域名")
    print_success(f"查询延迟范围: {min_delay}-{max_delay}秒")
    print_success(f"结果将保存到: {output_file}")
    print_info(f"注意: 程序会每10个结果自动保存一次临时文件")
    print("")
    
    print_info("按Enter键开始查询...")
    input()
    
    # 创建检查器实例并执行批量查询
    checker = BingIndexChecker(delay_range=(min_delay, max_delay), debug=debug_mode)
    try:
        checker.batch_check(domains, output_file)
    except KeyboardInterrupt:
        print_warning("\n程序被用户中断!")
    except Exception as e:
        print_error(f"\n程序出错: {str(e)}")
    
    print("")
    print_header("程序执行完毕!")
    print_info("感谢使用本工具！访问 blog.xiaoxinbk.cn 了解更多")
    input(f"{Colors.YELLOW}按Enter键退出...{Colors.ENDC}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n程序被用户中断!")
        # 已经在其他地方处理了结果保存
        input(f"{Colors.YELLOW}按Enter键退出...{Colors.ENDC}")
    except Exception as e:
        print_error(f"\n程序出错: {str(e)}")
        # 已经在其他地方处理了结果保存
        input(f"{Colors.YELLOW}按Enter键退出...{Colors.ENDC}")