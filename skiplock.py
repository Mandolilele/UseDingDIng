import os
import time
ADB_PATH = "/opt/homebrew/bin/adb"
print(">>>Unlocking screen")
    # 唤醒屏幕
result = os.system(f"{ADB_PATH} shell input keyevent KEYCODE_WAKEUP")
time.sleep(1)
# 滑动解锁（从屏幕底部向上滑动）
result = os.system(f"{ADB_PATH} shell input swipe 500 1500 500 500")
# time.sleep(3)

os.system(f"{ADB_PATH} shell input keyevent --longpress KEYCODE_VOLUME_UP")
time.sleep(0.1)
os.system(f"{ADB_PATH} shell input keyevent KEYCODE_POWER")
