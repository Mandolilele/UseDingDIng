import subprocess
import os

ADB_PATH = "/opt/homebrew/bin/adb"
device_ip = "192.168.1.130:5555"

# 使用subprocess执行adb connect命令
result = subprocess.run([ADB_PATH, "connect", device_ip], capture_output=True, text=True)
result = os.system(f"{ADB_PATH} shell input keyevent KEYCODE_WAKEUP")
# log(f"Wakeup result: {result}")
# time.sleep(1)
# 打印结果
print(result.stdout)
print(result.stderr)
