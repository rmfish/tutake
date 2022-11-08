from tutake.utils.config import tutake_config
import tushare as ts

if __name__ == '__main__':
    pro = ts.pro_api(tutake_config.get_tushare_token())
    df = pro.ggt_top10(**{
        "trade_date": '20211019'
    })
    print(df)
