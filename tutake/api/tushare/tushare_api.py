from tutake.utils.config import tutake_config
import tushare as ts

if __name__ == '__main__':
    pro = ts.pro_api(tutake_config.get_tushare_token())
    df = pro.hsgt_top10(**{
        "start_date": '20141102'
    })
    print(df)
