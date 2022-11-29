import pandas as pd
import tushare as ts

from tutake.utils.config import TutakeConfig

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)  # 显示列数
    pd.set_option('display.width', 1000)
    pro = ts.pro_api(TutakeConfig().get_tushare_token())
    df = pro.daily_basic()
    print(df)
