from tutake import task_api
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import file_dir

if __name__ == '__main__':
    task = task_api(TutakeConfig(file_dir(__file__)))
    task.start(True)  # 如果设置为True,则立即开始执行
