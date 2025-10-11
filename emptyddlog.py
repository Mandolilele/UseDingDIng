# 清空日志文件
with open("/tmp/dingdingclicker.log", "w") as log_file:
    log_file.write("")

# 日志记录函数
def log(message):
    with open("/tmp/dingdingclicker.log", "a") as log_file:
        log_file.write(f"{datetime.now()}: {message}\n")
