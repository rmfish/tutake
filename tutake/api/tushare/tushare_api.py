import pandas as pd
import tushare as ts

from tutake.utils.config import tutake_config

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)  # 显示列数
    pd.set_option('display.width', 1000)
    pro = ts.pro_api(tutake_config.get_tushare_token())
    df = pro.cashflow_vip(start_date='20100101', end_date='20200803')
    print(df)
