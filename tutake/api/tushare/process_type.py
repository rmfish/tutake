from enum import Enum


class ProcessType(Enum):
    HISTORY = 1  # 同步历史数据
    INCREASE = 2  # 同步增量数据
