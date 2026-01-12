'''
这段 Python 脚本旨在自动化钉钉 (DingDing) 应用的操作，通过模拟用户的点击操作，实现特定任务的自动化执行。
该脚本可以解锁设备屏幕、启动钉钉应用、执行指定的点击操作、关闭钉钉应用并熄灭屏幕。用户可以通过命令行参数设置上午和下午的基准时间，
脚本会在基准时间的前后一定范围内随机选择时间点执行任务。此外，脚本还支持日志记录功能，记录操作的详细信息。

主要功能
解锁屏幕：通过 ADB 命令解锁设备屏幕。
启动钉钉应用：使用 monkey 命令启动钉钉应用。
点击操作：在指定坐标位置模拟点击操作。
关闭钉钉应用：强制停止钉钉应用。
熄灭屏幕：模拟按下电源键熄灭屏幕。
随机时间执行：在指定基准时间的前后一定范围内随机选择时间点执行任务。
日志记录：记录每个步骤的详细信息到日志文件中。

v1.0 20240516
v1.1 加入了截屏确认发送邮件确认功能.还有防止程序反复被调用的功能
lee chuan
'''
import os
import time
import random
import argparse
import subprocess
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import pytesseract
from PIL import Image
# import psutil  # 确保已安装 psutil 库: pip install psutil

USEDELAYTIME = True
# USEDELAYTIME = False

useworkday = True
useworkday = False

# 钉钉应用的包名
DINGDING_PACKAGE = "com.alibaba.android.rimet"

# 需要点击的坐标,这个数据需要自己在手机工程模式下去找,比划一下就搞定了.
COORDINATES = [(433, 2206),(143,898), (560, 1400)] # for xiaomi 12 pro & 红米note 7 pro
# COORDINATES = [(433, 2206),(143,898)] # for xiaomi 12 pro & 红米note 7 pro
# COORDINATES = [(544, 2268),(150,980)] # for hongmi note 7 pro, 不实际打卡，只是关闭应用
# COORDINATES = [(531, 1700),(136,1022), (539, 1023)]  # for huawei
COORDINATES2 =[(775,1888),(551,2083)]   # for kill dingding app manual
# COORDINATES = [(544, 2268),(150,980)]

# adb 命令的绝对路径
ADB_PATH = "/opt/homebrew/bin/adb"

# 设备连接信息
DEVICE_IP = "10.0.0.156"
# DEVICE_IP = "192.168.40.122"
DEVICE_PORT = "5555"
device_ip = f"{DEVICE_IP}:{DEVICE_PORT}"

# 邮件配置
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 587
SMTP_USERNAME = '2955004@qq.com'
SMTP_PASSWORD = 'msdpjhiivheobjie'
EMAIL_FROM = '2955004@qq.com'
# EMAIL_TO = '2955004@qq.com'
EMAIL_TO = 'lichuan@cdcim.cn'
EMAIL_SUBJECT = 'DingDing Screenshot Result'

# 日志记录函数
def log(message):
    with open("/Users/mandoli/code/09DD/dingdingpylog.log", "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")

# 检查是否已有相同的脚本在运行
def is_already_running():
    script_name = os.path.basename(__file__)
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if script_name in proc.info['cmdline'] and proc.info['pid'] != os.getpid():
            return True
    return False

# 解锁屏幕
def unlock_screen(device_id=None):
    log("Unlocking screen")
    print(">>>Unlocking screen")
    # 唤醒屏幕
    device_option = f"-s {device_id} " if device_id else ""
    result = os.system(f"{ADB_PATH} {device_option}shell input keyevent KEYCODE_WAKEUP")
    log(f"Wakeup result: {result}")
    time.sleep(1)
    # 滑动解锁（从屏幕底部向上滑动）
    result = os.system(f"{ADB_PATH} {device_option}shell input swipe 500 1500 500 500")
    log(f"Swipe result: {result}")
    time.sleep(3)

# 启动钉钉应用
def launch_dingding(device_id=None):
    log(f"Launching DingDing")
    print(">>>Launching DingDing")
    device_option = f"-s {device_id} " if device_id else ""
    result = os.system(f"{ADB_PATH} {device_option}shell monkey -p {DINGDING_PACKAGE} -c android.intent.category.LAUNCHER 1")
    log(f"Launch result: {result}")
    time.sleep(10)  # 等待应用启动

# 点击指定坐标
def click_coordinates(cor1, device_id=None):
    device_option = f"-s {device_id} " if device_id else ""
    for x, y in cor1:
        log(f"Clicking coordinates ({x}, {y})")
        print(f">>>Clicking coordinates ({x}, {y})")
        result = os.system(f"{ADB_PATH} {device_option}shell input tap {x} {y}")
        log(f"Click result: {result}")
        time.sleep(15)  # 等待n秒以避免操作太快

# 截图
def take_screenshot(device_id=None):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    screenshot_path = f"/Users/mandoli/code/09DD/screenshot/screenshot_{timestamp}.png"
    log(f"Taking screenshot: {screenshot_path}")
    print(f">>>Taking screenshot: {screenshot_path}")
    device_option = f"-s {device_id} " if device_id else ""
    result = os.system(f"{ADB_PATH} {device_option}shell screencap -p /sdcard/screenshot.png")
    log(f"Screencap result: {result}")
    result = os.system(f"{ADB_PATH} {device_option}pull /sdcard/screenshot.png {screenshot_path}")
    log(f"Pull result: {result}")
    return screenshot_path

def check_success_in_screenshot(image_path):
    """检查截图中是否包含'打卡成功'字样"""
    try:
        # Set TESSDATA_PREFIX to point to Homebrew's tessdata directory
        os.environ['TESSDATA_PREFIX'] = '/opt/homebrew/share/tessdata'
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='chi_sim')
        log(f"OCR识别结果: {text}")
        print(f">>>OCR识别结果: {text}")
        return "功" in text
    except Exception as e:
        log(f"OCR识别失败: {e}")
        print(f">>>OCR识别失败: {e}")
        return False

# 发送邮件
def send_email_with_screenshot(screenshot_path, mailtext):
    msg = EmailMessage()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    print("mailtext:"+mailtext)
    if "功" in mailtext:  # 打卡成功
        msg['Subject'] = "DDDone"
        msg.set_content(mailtext)
        # msg.set_content("打卡成功")
    else:  # 打卡失败
        msg['Subject'] = "UnDone"
        msg.set_content(f"打卡失败\n{mailtext}")
        # 失败时附加截图以便查看问题
        if os.path.exists(screenshot_path):
            with open(screenshot_path, 'rb') as f:
                img_data = f.read()
                msg.add_attachment(img_data, maintype='image', 
                                 subtype='png', 
                                 filename=os.path.basename(screenshot_path))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        log(f"Failed to send email: {e}")
        print(f">>>Failed to send email: {e}")
    else:
        log("Email sent successfully")
        print(">>>Email sent")

# 杀掉钉钉应用
def kill_dingding(device_id=None):
    log(f"Killing DingDing")
    print(">>>Killing DingDing")
    device_option = f"-s {device_id} " if device_id else ""
    result = os.system(f"{ADB_PATH} {device_option}shell am force-stop {DINGDING_PACKAGE}")
    log(f"Kill result: {result}")
    print(f">>>Killed result: {result}")
    return result

# 熄灭屏幕
def turn_off_screen(device_id=None):
    log(f"Turning off screen at {datetime.now()}")
    print(">>>Turning off screen")
    device_option = f"-s {device_id} " if device_id else ""
    result = os.system(f"{ADB_PATH} {device_option}shell input keyevent KEYCODE_POWER")
    log(f"Screen off result: {result}")

# 生成随机时间，确保不在指定时间点
def get_random_time(base_time, minute_range, exclude_minute):
    while True:
        minute = (base_time.minute + random.randint(*minute_range)) % 60
        second = random.randint(0, 59)
        random_time = base_time.replace(minute=minute, second=second, microsecond=0)
        if random_time.minute != exclude_minute:
            return random_time

# 测试 USB 连接
def test_usb_connection():
    """测试 USB 连接"""
    log("测试 USB 连接...")
    print(">>>测试 USB 连接...")
    
    # 列出已连接的设备
    result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
    log(f"已连接设备列表:\n{result.stdout}")
    
    # 查找USB设备（非WiFi设备）
    lines = result.stdout.strip().split('\n')
    usb_device = None
    for line in lines[1:]:  # 跳过第一行标题
        if line and not device_ip in line and "device" in line:
            usb_device = line.split()[0]  # 获取设备ID
            break
    
    if usb_device:
        log(f"USB 连接成功！设备ID: {usb_device}")
        print(f">>>USB 连接成功！设备ID: {usb_device}")
        return usb_device  # 返回设备ID而不是布尔值
    else:
        log("USB 连接失败或未检测到USB设备")
        print(">>>USB 连接失败或未检测到USB设备")
        return None  # 返回None表示没有找到USB设备

# 测试 WiFi 连接
def test_wifi_connection():
    """测试 WiFi 连接"""
    log("测试 WiFi 连接...")
    print(">>>测试 WiFi 连接...")
    
    # 断开所有连接
    os.system(f"{ADB_PATH} disconnect")
    
    # 尝试通过 WiFi 连接
    result = subprocess.run([ADB_PATH, "connect", device_ip], capture_output=True, text=True)
    log(f"WiFi 连接结果: {result.stdout}")
    print(f">>>WiFi 连接结果: {result.stdout}")
    
    if "connected to" in result.stdout:
        # 确认设备已连接
        time.sleep(1)  # 等待连接稳定
        devices_result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
        if device_ip in devices_result.stdout:
            log(f"WiFi 连接成功！设备ID: {device_ip}")
            print(f">>>WiFi 连接成功！设备ID: {device_ip}")
            return device_ip  # 返回设备ID
        else:
            log("WiFi 设备连接成功但未在设备列表中找到")
            print(">>>WiFi 设备连接成功但未在设备列表中找到")
            return None
    else:
        log("WiFi 连接失败")
        print(">>>WiFi 连接失败")
        return None

# 执行打卡流程
def perform_clock_in(device_id=None):
    screenshot_path = ""
    unlock_screen(device_id)
    kill_dingding_result = kill_dingding(device_id)
    time.sleep(2)
    # click_coordinates(COORDINATES2, device_id) #用手动方式关闭钉钉
    if kill_dingding_result == 0:
        mailtext = "the DingDing has been killed successfully"
    else:
        mailtext = "the DingDing could not be killed successfully"
    # unlock_screen(device_id)
    launch_dingding(device_id)
    click_coordinates(COORDINATES, device_id) # 点击坐标进行打卡
    time.sleep(8)
    screenshot_path = take_screenshot(device_id) # 截图
    
    # 检查打卡是否成功，最多重试3次
    max_retries = 3
    for retry in range(max_retries):
        if check_success_in_screenshot(screenshot_path):
            mailtext = f"打卡成功 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            log("打卡成功确认")
            print(">>>打卡成功确认")
            break
        else:
            log(f"未检测到打卡成功，重试中 ({retry + 1}/{max_retries})")
            print(f">>>未检测到打卡成功，重试中 ({retry + 1}/{max_retries})")
            if retry < max_retries - 1:
                # 重新执行打卡流程
                kill_dingding(device_id)
                time.sleep(2)
                # 添加解锁屏幕步骤
                unlock_screen(device_id)
                launch_dingding(device_id)
                click_coordinates(COORDINATES, device_id)
                time.sleep(8)
                screenshot_path = take_screenshot(device_id)  # 更新截图路径

    if retry == max_retries - 1:  # 所有重试都失败
        mailtext = f"打卡失败 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    kill_dingding_result = kill_dingding(device_id)
    time.sleep(2)
    # click_coordinates(COORDINATES2, device_id) #用手动方式关闭钉钉
    # if kill_dingding_result == 0:
    #     mailtext = "the DingDing has been killed successfully"
    # else:
    #     mailtext = "the DingDing could not be killed successfully"
    send_email_with_screenshot(screenshot_path, mailtext) # 发送邮件
    turn_off_screen(device_id)
    return True

# 主函数
def main(morning_base, evening_base):
    now = datetime.now()

    # 检查是否为工作日（星期一到星期五）
    if now.weekday() >= 5 and useworkday:
        log("Today is not a weekday. Exiting.")
        print(">>>Today is not a weekday. Exiting.")
        return

    log("Script started")
    print(">>>Script started")

    # 生成上午随机时间，范围在基准时间的前后10分钟之间
    morning_time = get_random_time(morning_base, (-2, 2), 59)
    log(f"Morning time scheduled at {morning_time}")
    print(f"Morning time scheduled at {morning_time}")

    # 生成下午随机时间，范围在基准时间的前后10分钟之间
    evening_time = get_random_time(evening_base, (-2, 2), None)
    log(f"Evening time scheduled at {evening_time}")
    print(f"Evening time scheduled at {evening_time}")

    if USEDELAYTIME:
        if now < morning_time:
            log(f"Waiting until {morning_time}")
            time.sleep((morning_time - now).total_seconds())
        elif now < evening_time:
            log(f"Waiting until {evening_time}")
            time.sleep((evening_time - now).total_seconds())
        else:
            log("Current time is outside scheduled range")
            # return

    # 首先尝试USB连接
    log("尝试通过USB连接设备...")
    print(">>>尝试通过USB连接设备...")
    usb_device_id = test_usb_connection()
    if usb_device_id:
        log(f"使用USB连接执行打卡流程，设备ID: {usb_device_id}")
        print(f">>>使用USB连接执行打卡流程，设备ID: {usb_device_id}")
        if perform_clock_in(usb_device_id):
            log("Script finished successfully via USB")
            print(">>>Script finished successfully via USB")
            return
    
    # 如果USB连接失败，尝试WiFi连接
    log("尝试通过WiFi连接设备...")
    print(">>>尝试通过WiFi连接设备...")
    for attempt in range(5):  # 尝试WiFi连接最多5次
        wifi_device_id = test_wifi_connection()
        if wifi_device_id:
            log(f"使用WiFi连接执行打卡流程，设备ID: {wifi_device_id}")
            print(f">>>使用WiFi连接执行打卡流程，设备ID: {wifi_device_id}")
            if perform_clock_in(wifi_device_id):
                log("Script finished successfully via WiFi")
                print(">>>Script finished successfully via WiFi")
                return
            break  # 如果连接成功但执行失败，不再重试
        else:
            log(f"WiFi连接尝试 {attempt + 1}/5 失败，重试中...")
            print(f">>>WiFi连接尝试 {attempt + 1}/5 失败，重试中...")
            
            # 清理动作
            log("执行清理操作")
            print(">>>执行清理操作")
            os.system(f"{ADB_PATH} disconnect")  # 断开所有连接
            os.system(f"{ADB_PATH} kill-server")  # 停止 ADB 服务
            os.system(f"{ADB_PATH} start-server")  # 重启 ADB 服务
            time.sleep(2)  # 等待2秒后重试

    # 如果所有连接方式都失败
    log("所有连接方式均失败")
    print(">>>所有连接方式均失败")
    send_email_with_screenshot("", f"无法连接设备，USB和WiFi({device_ip})连接均失败")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run DingDing automation script with specified base times.')
    parser.add_argument('--morning', type=str, help='Base time for morning in HH:MM format')
    parser.add_argument('--evening', type=str, help='Base time for evening in HH:MM format')
    args = parser.parse_args()

    # 设置默认基准时间
    if args.morning:
        morning_base = datetime.strptime(args.morning, '%H:%M').replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
    else:
        # 默认上午基准时间为 08:30
        morning_base = datetime.now().replace(hour=8, minute=10, second=0, microsecond=0)

    if args.evening:
        evening_base = datetime.strptime(args.evening, '%H:%M').replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
    else:
        # 默认下午基准时间为 17:45
        evening_base = datetime.now().replace(hour=17, minute=40, second=0, microsecond=0)

    main(morning_base, evening_base)
