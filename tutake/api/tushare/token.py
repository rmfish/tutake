from tutake.utils.config import config
import tushare as ts


def is_useful_token(token):
    pro = ts.pro_api(token)
    try:
        df = pro.stock_basic(limit=100)
        if df.shape[0] == 100:
            return True
    except Exception as err:
        # print("{} {}".format(token, err))
        return False


def is_2000_token(token):
    pro = ts.pro_api(token)
    try:
        df = pro.stk_managers(ts_code='000001.SZ')
        if df.shape[0] >= 1:
            return True
    except Exception as err:
        return False


def is_5000_token(token):
    pro = ts.pro_api(token)
    try:
        df = pro.ggt_monthly(trade_date='201906')
        if df.shape[0] >= 1:
            return True
    except Exception as err:
        return False


if __name__ == '__main__':
    tokens = set(config['tushare']['tokens'])
    print("Token 总数 %d" % len(tokens))
    for i in tokens:
        if is_useful_token(i):
            if is_2000_token(i):
                if is_5000_token(i):
                    print("- {} # 5000".format(i))
                else:
                    print("- {} # 2000".format(i))
            else:
                print("- {} # 120".format(i))
