import os
import time
import random
from datetime import datetime

# 钉钉应用的包名
DINGDING_PACKAGE = "com.alibaba.android.rimet"

# 需要点击的坐标
COORDINATES = [(750, 358), (560, 1400)]

# 日志记录函数
def log(message):
    with open("/tmp/dingdingclicker.log", "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")

# 解锁屏幕
def unlock_screen():
    log("Unlocking screen")
    print("Unlocking screen")
    # 唤醒屏幕
    os.system("adb shell input keyevent KEYCODE_WAKEUP")
    time.sleep(1)
    # 滑动解锁（从屏幕底部向上滑动）
    os.system("adb shell input swipe 500 1500 500 500")
    time.sleep(1)

# 启动钉钉应用
def launch_dingding():
    log("Launching DingDing")
    print("Launching DingDing")
    result = os.system(f"adb shell monkey -p {DINGDING_PACKAGE} -c android.intent.category.LAUNCHER 1")
    log(f"Launch result: {result}")
    time.sleep(5)  # 等待应用启动

# 点击指定坐标
def click_coordinates():
    for x, y in COORDINATES:
        log(f"Clicking coordinates ({x}, {y})")
        print(f"Clicking coordinates ({x}, {y})")
        result = os.system(f"adb shell input tap {x} {y}")
        log(f"Click result: {result}")
        print(f"Click result: {result}")
        time.sleep(2)  # 等待一秒以避免操作太快

# 生成随机时间，确保不在 8:59 这个时间点
def get_random_time(hour, minute_range, exclude_minute):
    while True:
        minute = random.randint(*minute_range)
        second = random.randint(0, 59)
        if minute != exclude_minute:
            return datetime.now().replace(hour=hour, minute=minute, second=second, microsecond=0)

# 主函数
def main():
    now = datetime.now()
    log("Script started")
    print("Script started")

    # 临时直接执行任务，不进行等待
    unlock_screen()
    launch_dingding()
    click_coordinates()

    log("Script finished")
    print("Script finished")

if __name__ == "__main__":
    main()
