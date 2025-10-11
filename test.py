import unittest
import os
import subprocess
from datetime import datetime
import test_adb_connection

class TestDingDingAutomation(unittest.TestCase):
    def setUp(self):
        self.adb_path = "/opt/homebrew/bin/adb"
        self.device_ip = "10.0.0.156:5555"
        
    def test_adb_installation(self):
        """测试 ADB 是否正确安装"""
        result = subprocess.run([self.adb_path, "version"], capture_output=True, text=True)
        self.assertIn("Android Debug Bridge", result.stdout)
        
    def test_device_connection(self):
        """测试设备连接"""
        # 测试 WiFi 连接
        wifi_result = test_adb_connection.test_wifi_connection()
        self.assertTrue(wifi_result, "WiFi 连接失败")
        
        # 测试 USB 连接
        usb_result = test_adb_connection.test_usb_connection()
        self.assertTrue(usb_result or wifi_result, "所有连接方式都失败")
        
    def test_screenshot_directory(self):
        """测试截图目录是否存在"""
        screenshot_dir = "/Users/mandoli/code/09DD/screenshot"
        self.assertTrue(os.path.exists(screenshot_dir), "截图目录不存在")
        
    def test_log_file(self):
        """测试日志文件"""
        log_file = "/Users/mandoli/code/09DD/dingdingpylog.log"
        if not os.path.exists(log_file):
            with open(log_file, "w") as f:
                f.write(f"{datetime.now()}: Test log file created\n")
        self.assertTrue(os.path.exists(log_file), "日志文件不存在")
        
    def test_adb_commands(self):
        """测试基本的 ADB 命令"""
        # 测试 adb devices 命令
        result = subprocess.run([self.adb_path, "devices"], capture_output=True, text=True)
        self.assertIsNotNone(result.stdout)
        
        # 测试连接设备
        result = subprocess.run([self.adb_path, "connect", self.device_ip], capture_output=True, text=True)
        self.assertIn("connected", result.stdout.lower() + result.stderr.lower())

if __name__ == '__main__':
    unittest.main(verbosity=2)