import tutake as ts


def process():
    pro = ts.process_api("tushare_token")
    print(pro.shibor())


def query():
    pro = ts.pro_api()
    print(pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date'))
    print(pro.stock_basic(limit=100))


if __name__ == '__main__':
    query()
    # 如果增加tushare_token 则支持使用Tushare进行Failover，未实现的函数依然调用tushare
