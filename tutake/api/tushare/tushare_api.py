from tutake.utils.config import tutake_config
import tushare as ts

if __name__ == '__main__':
    pro = ts.pro_api(tutake_config.get_tushare_token())
    df = pro.moneyflow_hsgt(**{
        "start_date": '201400825', "end_date": '20141208'
    })
    print(df)
