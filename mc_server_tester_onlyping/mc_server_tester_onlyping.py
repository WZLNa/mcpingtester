import socket
import concurrent.futures
import os
import time
import sys
from datetime import datetime

# 全局配置
SIGNATURE = "By.wzln 25/8/30"
TIMEOUT = 3.0  # 3秒超时
PORT = 25565  # Minecraft服务器端口
MAX_WORKERS = 3  # 最大并行数
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
            
            return (target, True, latency)
    
    except Exception as e:
        return (target, False, float('inf'))

def get_targets():
    """获取目标服务器列表（优先使用targets.txt，否则使用默认列表）"""
    # 检查当前目录下的目标文件
    if os.path.exists("targets.txt"):
        try:
            with open("targets.txt", "r") as f:
                targets = [line.strip() for line in f.readlines() if line.strip()]
            
            if targets:
                return targets
        except Exception:
            pass
    
    # 如果没有目标文件或读取失败，使用默认列表
    return DEFAULT_TARGETS

def save_results(results):
    """保存结果到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mc_servers_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(f"# Minecraft可用服务器列表\n")
        f.write(f"# 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 签名: {SIGNATURE}\n\n")
        
        for i, (target, status, latency) in enumerate(results, 1):
            if status:
                f.write(f"{i}. {target}: {latency} ms\n")
    
    return filename

def main():
    """主程序"""
    print(f"\n{'=' * 50}")
    print(f"Minecraft 服务器测试工具 {SIGNATURE}")
    print(f"测试端口: {PORT} | 最大并行数: {MAX_WORKERS}")
    print(f"{'=' * 50}\n")
    
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
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(test_server, target): target for target in targets}
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            
            target = result[0]
            if result[1]:  # 成功
                print(f"  ✓ {target}: 可用 (延迟: {result[2]} ms)")
            else:  # 失败
                print(f"  ✗ {target}: 不可用")
    
    # 计算耗时
    elapsed = time.time() - start_time
    
    # 筛选可用服务器
    available_servers = [r for r in results if r[1]]
    available_servers.sort(key=lambda x: x[2])  # 按延迟排序
    
    print(f"\n{'=' * 30}")
    print(f"测试完成! 耗时: {elapsed:.2f}秒")
    print(f"可用服务器数量: {len(available_servers)}/{len(targets)}")
    print(f"{'=' * 30}\n")
    
    # 输出结果
    if available_servers:
        print("推荐服务器 (按延迟排序):")
        for i, (target, status, latency) in enumerate(available_servers, 1):
            print(f"  {i}. {target}: {latency} ms")
        
        # 保存结果
        result_file = save_results(available_servers)
        print(f"\n结果已保存到: {result_file}")
    else:
        print("警告: 未找到可用服务器")
    
    # 结束提示
    print(f"\n{'=' * 50}")
    print(f"{SIGNATURE}")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 50}")
    
    # 保持窗口打开
    if getattr(sys, 'frozen', False):  # 如果是EXE文件
        input("\n按Enter键退出...")
    else:
        print("\n程序执行完毕")

if __name__ == "__main__":
    main()
