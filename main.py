from tutake import task_api

if __name__ == '__main__':
    task = task_api("./config.yml")
    task.start(True)  # 如果设置为True,则立即开始执行
