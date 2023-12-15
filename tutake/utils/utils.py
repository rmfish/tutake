import os
from datetime import timedelta, datetime

import pytz


def file(dir, file_name):
    return os.path.join(dir, file_name)


def file_dir(file_path):
    """
    获得file文件的所属目录
    :param file_path:
    :return:
    """
    return os.path.dirname(os.path.realpath(file_path))


def realpath(file):
    """
    获取真实路径
    :param file:
    :return:
    """
    path = str(file)
    if path.startswith("~"):
        return os.path.expanduser(path)
    return os.path.realpath(path)


def project_root():
    """
    获取项目的根路径
    :return:
    """
    return realpath("{}/../../".format(file_dir(__file__)))


def start_of_day(timezone="Asia/Shanghai"):
    tz = pytz.timezone(timezone)
    today = datetime.now(tz=tz)
    return today.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(timezone="Asia/Shanghai"):
    return start_of_day(timezone) + timedelta(1)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == "__main__":
    print(file(project_root(), "utils.py"))
