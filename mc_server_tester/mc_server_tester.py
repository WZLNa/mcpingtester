import socket
import concurrent.futures
import os
import time
import sys
import traceback
from datetime import datetime

# 全局配置
SIGNATURE = "By.wzln 25/8/30"
TIMEOUT = 3.0  # 3秒超时
PORT = 25565  # Minecraft服务器端口
MAX_WORKERS = 3  # 最大并行数
TEST_COUNT = 3  # 每个服务器的测试次数，用于计算丢包率

# 日志文件路径
LOG_FILE = "server_test_log.txt"

def log_message(message):
    """将消息记录到日志文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        # 如果无法写入日志文件，尝试输出到控制台
        print(f"无法写入日志文件: {e}")
        print(log_entry)

def setup_logging():
    """设置日志文件"""
    try:
        # 清空或创建日志文件
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(f"Minecraft服务器测试日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
    except Exception as e:
        print(f"无法创建日志文件: {e}")

# 默认目标列表保持不变
DEFAULT_TARGETS = [
    "mc.hypixel.net",  # 大型MC服务器
    "hy.hypixel.com.cn",
    "Hypixel-1.xuegao123.xyz",
    "MC.HYPIXEL.CC",
    "SJ.HY.HYPIXEL.COM.CN",
    "LG.HY.HYPIXEL.COM.CN",
    "MC.Hypixel.CN",
    "Hyp.Jiasu.Ru",
    "MC.HYPIXEL.WIN",
    "mc.yuanshen.us",
    "hypszj.laoxienet.xyz",
    "Hyp-1.JiaSu.Ru",
    "free.voic.fun",
    "sh.yuanshen.us",
    "MC.MCHYP.TOP",
    "B.Hypixel.CN",
    "Hyp-2.JiaSu.Ru",
    "Hyp-3.Jiasu.Ru",
    "hypixel.scarefree.cn",
    "sqbgp.yuanshen.us",
    "gz.yuanshen.us",
    "free.voic.fun",
    "us.lfcup.cn",
    "cn2.lfcup.cn",
    "hk.lfcup.cn",
    "hk2.lfcup.cn",
    "sz.lfcup.cn",
    "sh-jp-pro.jsip.top",
    "Hyp-1.xuegao123.xyz",
    "china.hypixel.su",
    "HK.HY.HYPIXEL.COM.CN",
    "sq.jsip.club",
    "hypixel.net.hypixel.su",
    "hypixel.cyou",
    "Cmcc.IPV6.BETA.hypixel.su",
    "hyp-2.xuegao123.xyz",
    "hyp-3.xuegao123.xyz",
    "free.naboost.site",
    "connect.hypixel.run",
    "mc.jsip.lol",
    "hk.hypixel.click",
    "ncp.hight.cloud",
    "sh.hypixel.cn",
    "hyp.quickproxy.top",
    "A.Hypixel.CN",
    "as.minemen.cn",
    "hoplite.mchyp.top",
    "mc.hypixel.best",
    "mmc.mchyp.top",
    "sh1.390001.xyz",
    "la.jsip.top",
    "sh-jp.jsip.top"
]

def test_server(target):
    """测试单个Minecraft服务器连接"""
    success_count = 0
    total_latency = 0
    min_latency = float('inf')
    
    try:
        for i in range(TEST_COUNT):
            try:
                # 解析目标格式 (支持IP:PORT)
                if ":" in target:
                    host, port_str = target.split(":", 1)
                    port = int(port_str)
                else:
                    host = target
                    port = PORT
                
                # 创建TCP套接字
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(TIMEOUT)
                    
                    start_time = time.time()
                    sock.connect((host, port))
                    latency = round((time.time() - start_time) * 1000, 2)  # 毫秒
                    
                    # 尝试获取服务器响应（可选）
                    try:
                        sock.send(b"\xFE\x01")  # Minecraft服务器列表ping
                        response = sock.recv(1024)
                        # 可以解析响应获取更多服务器信息
                    except:
                        pass
                    
                    success_count += 1
                    total_latency += latency
                    if latency < min_latency:
                        min_latency = latency
                    
                    # 短暂延迟，避免过于频繁的请求
                    if i < TEST_COUNT - 1:
                        time.sleep(0.1)
            
            except Exception as e:
                # 短暂延迟，避免过于频繁的请求
                if i < TEST_COUNT - 1:
                    time.sleep(0.1)
                continue
        
        # 计算丢包率和平均延迟
        packet_loss = round((1 - success_count / TEST_COUNT) * 100, 2) if TEST_COUNT > 0 else 100
        avg_latency = round(total_latency / success_count, 2) if success_count > 0 else float('inf')
        
        return (target, success_count > 0, avg_latency, min_latency, packet_loss)
    
    except Exception as e:
        error_msg = f"测试 {target} 时发生未预期的错误: {str(e)}"
        log_message(error_msg)
        return (target, False, float('inf'), float('inf'), 100.0)

def get_targets():
    """获取目标服务器列表（优先使用targets.txt，否则使用默认列表）"""
    try:
        # 检查当前目录下的目标文件
        if os.path.exists("targets.txt"):
            try:
                with open("targets.txt", "r", encoding="utf-8") as f:
                    targets = [line.strip() for line in f.readlines() if line.strip()]
                
                if targets:
                    log_message(f"从targets.txt加载了 {len(targets)} 个目标")
                    return targets
            except Exception as e:
                log_message(f"读取targets.txt时出错: {e}")
        
        # 如果没有目标文件或读取失败，使用默认列表
        log_message(f"使用默认目标列表，共 {len(DEFAULT_TARGETS)} 个目标")
        return DEFAULT_TARGETS
    
    except Exception as e:
        log_message(f"获取目标列表时出错: {e}")
        return DEFAULT_TARGETS

def save_results(results):
    """保存结果到文件"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mc_servers_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Minecraft可用服务器列表\n")
            f.write(f"# 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 签名: {SIGNATURE}\n")
            f.write(f"# 每个服务器测试次数: {TEST_COUNT}\n\n")
            
            for i, (target, status, avg_latency, min_latency, packet_loss) in enumerate(results, 1):
                if status:
                    f.write(f"{i}. {target}: 平均延迟 {avg_latency} ms, 最低延迟 {min_latency} ms, 丢包率 {packet_loss}%\n")
        
        log_message(f"结果已保存到: {filename}")
        return filename
    
    except Exception as e:
        log_message(f"保存结果时出错: {e}")
        return None

def main():
    """主程序"""
    try:
        # 设置日志
        setup_logging()
        log_message("程序启动")
        
        # 如果是EXE文件，更改工作目录到EXE所在目录
        if getattr(sys, 'frozen', False):
            os.chdir(os.path.dirname(sys.executable))
            log_message(f"工作目录已更改为: {os.getcwd()}")
        
        print(f"\n{'=' * 50}")
        print(f"Minecraft 服务器测试工具 {SIGNATURE}")
        print(f"测试端口: {PORT} | 最大并行数: {MAX_WORKERS}")
        print(f"每个服务器测试次数: {TEST_COUNT}")
        print(f"{'=' * 50}\n")
        
        log_message("程序界面初始化完成")
        
        # 获取目标列表
        targets = get_targets()
        
        print(f"已加载 {len(targets)} 个服务器:")
        for i, target in enumerate(targets, 1):
            print(f"  {i}. {target}")
        
        # 并行测试
        print(f"\n{'=' * 30}")
        print("开始测试服务器连通性...")
        print(f"{'=' * 30}\n")
        
        results = []
        start_time = time.time()
        
        log_message(f"开始测试 {len(targets)} 个服务器")
        
        # 使用更简单的线程池处理方式
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # 提交所有任务
            future_to_target = {executor.submit(test_server, target): target for target in targets}
            
            # 处理完成的任务
            completed = 0
            for future in concurrent.futures.as_completed(future_to_target):
                try:
                    result = future.result(timeout=TIMEOUT * TEST_COUNT + 10)  # 增加超时时间
                    results.append(result)
                    completed += 1
                    
                    target, status, avg_latency, min_latency, packet_loss = result
                    if status:  # 成功
                        msg = f"  ✓ {target}: 可用 (平均延迟: {avg_latency} ms, 最低延迟: {min_latency} ms, 丢包率: {packet_loss}%)"
                        print(msg)
                        log_message(msg)
                    else:  # 失败
                        msg = f"  ✗ {target}: 不可用 (丢包率: {packet_loss}%)"
                        print(msg)
                        log_message(msg)
                        
                    # 显示进度
                    print(f"进度: {completed}/{len(targets)}")
                        
                except concurrent.futures.TimeoutError:
                    target = future_to_target[future]
                    error_msg = f"测试 {target} 超时"
                    print(error_msg)
                    log_message(error_msg)
                    results.append((target, False, float('inf'), float('inf'), 100.0))
                except Exception as e:
                    target = future_to_target[future]
                    error_msg = f"处理测试结果时出错: {str(e)}\n{traceback.format_exc()}"
                    print(error_msg)
                    log_message(error_msg)
                    results.append((target, False, float('inf'), float('inf'), 100.0))
        
        # 计算耗时
        elapsed = time.time() - start_time
        
        # 筛选可用服务器
        available_servers = [r for r in results if r[1]]
        available_servers.sort(key=lambda x: (x[4], x[2]))  # 先按丢包率排序，再按平均延迟排序
        
        print(f"\n{'=' * 30}")
        print(f"测试完成! 耗时: {elapsed:.2f}秒")
        print(f"可用服务器数量: {len(available_servers)}/{len(targets)}")
        print(f"{'=' * 30}\n")
        
        log_message(f"测试完成，耗时: {elapsed:.2f}秒，可用服务器: {len(available_servers)}/{len(targets)}")
        
        # 输出结果
        if available_servers:
            print("推荐服务器 (按丢包率和延迟排序):")
            for i, (target, status, avg_latency, min_latency, packet_loss) in enumerate(available_servers, 1):
                print(f"  {i}. {target}: 平均延迟 {avg_latency} ms, 最低延迟 {min_latency} ms, 丢包率 {packet_loss}%")
            
            # 保存结果
            result_file = save_results(available_servers)
            if result_file:
                print(f"\n结果已保存到: {result_file}")
            else:
                print("\n警告: 保存结果失败")
        else:
            print("警告: 未找到可用服务器")
            log_message("警告: 未找到可用服务器")
        
        # 结束提示
        print(f"\n{'=' * 50}")
        print(f"{SIGNATURE}")
        print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 50}")
        
        log_message("程序正常结束")
        
        # 保持窗口打开
        if getattr(sys, 'frozen', False):  # 如果是EXE文件
            input("\n按Enter键退出...")
        else:
            print("\n程序执行完毕")
    
    except Exception as e:
        error_msg = f"程序执行过程中发生未预期的错误: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        log_message(error_msg)
        
        # 保持窗口打开以便查看错误
        if getattr(sys, 'frozen', False):  # 如果是EXE文件
            input("\n按Enter键退出...")

if __name__ == "__main__":
    main()