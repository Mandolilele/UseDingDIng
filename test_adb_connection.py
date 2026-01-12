import os
import subprocess
import time

# ADB 路径
ADB_PATH = "/opt/homebrew/bin/adb"

# 设备信息
DEVICE_IP = "192.168.0.100"
DEVICE_PORT = "5555"
DEVICE_USB = "device_serial_number"  # 需要替换为实际的设备序列号

def log_message(message):
    print(f">>> {message}")
    
def test_usb_connection():
    """测试 USB 连接"""
    log_message("测试 USB 连接...")
    
    # 列出已连接的设备
    result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
    log_message(f"已连接设备列表:\n{result.stdout}")
    
    if "device" in result.stdout:
        # 点亮屏幕
        os.system(f"{ADB_PATH} shell input keyevent KEYCODE_WAKEUP")
        time.sleep(1)
        log_message("USB 连接成功！屏幕已点亮")
        return True
    else:
        log_message("USB 连接失败")
        return False

def test_wifi_connection():
    """测试 WiFi 连接"""
    log_message("测试 WiFi 连接...")
    
    # 断开所有连接
    os.system(f"{ADB_PATH} disconnect")
    
    # 尝试通过 WiFi 连接
    device_address = f"{DEVICE_IP}:{DEVICE_PORT}"
    result = subprocess.run([ADB_PATH, "connect", device_address], capture_output=True, text=True)
    log_message(f"WiFi 连接结果: {result.stdout}")
    
    if "connected to" in result.stdout:
        # 点亮屏幕
        os.system(f"{ADB_PATH} shell input keyevent KEYCODE_WAKEUP")
        time.sleep(1)
        log_message("WiFi 连接成功！屏幕已点亮")
        return True
    else:
        log_message("WiFi 连接失败")
        return False

def test_adb_commands():
    """测试基本的 ADB 命令"""
    log_message("测试基本 ADB 命令...")
    
    # 测试获取设备状态
    result = subprocess.run([ADB_PATH, "get-state"], capture_output=True, text=True)
    log_message(f"设备状态: {result.stdout}")
    
    # 测试获取设备信息
    result = subprocess.run([ADB_PATH, "shell", "getprop", "ro.product.model"], capture_output=True, text=True)
    log_message(f"设备型号: {result.stdout}")

def main():
    log_message("开始 ADB 连接测试...")
    
    # 测试 USB 连接
    usb_success = test_usb_connection()
    
    # 测试 WiFi 连接
    wifi_success = test_wifi_connection()
    
    # 如果任一连接成功，测试基本命令
    if usb_success or wifi_success:
        test_adb_commands()
    
    log_message("ADB 连接测试完成")

if __name__ == "__main__":
    main()