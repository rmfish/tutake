import pandas as pd

from tutake.utils.config import tutake_config
import tushare as ts

if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)  # 显示列数
    pd.set_option('display.width', 1000)
    pro = ts.pro_api(tutake_config.get_tushare_token())
    df = pro.express_vip(**{

    })
    print(df)
