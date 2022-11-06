from abc import ABCMeta, abstractmethod
from enum import Enum


class ProcessType(Enum):
    HISTORY = 1  # 同步历史数据
    INCREASE = 2  # 同步增量数据


class DataProcess(metaclass=ABCMeta):
    @abstractmethod
    def prepare(self, process_type: ProcessType): pass

    """
    同步历史数据准备工作
    :return:
    """

    @abstractmethod
    def tushare_parameters(self, process_type: ProcessType) -> list: pass

    @abstractmethod
    def param_loop_process(self, process_type: ProcessType, **params) -> dict: pass
