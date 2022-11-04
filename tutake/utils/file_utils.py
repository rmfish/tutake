import os


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
    return os.path.realpath(file)


def project_root():
    """
    获取项目的根路径
    :return:
    """
    return realpath("{}/../../".format(file_dir(__file__)))


if __name__ == "__main__":
    print(file(project_root(), "file_utils.py"))
