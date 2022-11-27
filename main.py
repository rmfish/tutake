import tutake

if __name__ == '__main__':
    api = tutake.pro_api(
        data_dir='/Users/rmfish/Library/Mobile Documents/com~apple~CloudDocs/Database/5_Data/Quant/data')
    print(tutake.pro_bar(api, ts_code='000002.SZ', adj='qfq'))

    # task = task_api(TutakeConfig(file_dir(__file__)))
    # task.start(True)  # 如果设置为True,则立即开始执行
