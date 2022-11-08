from tutake.utils.config import tutake_config
import tushare as ts

if __name__ == '__main__':
    pro = ts.pro_api(tutake_config.get_tushare_token())
    df = pro.ggt_monthly(**{

    })
    print(df)
