import json

import tutake as tt


class Test(object):
    def __init__(self):
        self.api = tt.Tutake("../config.yml").tushare_api()

    def meta_query(self):
        print(json.dumps(self.api._stock_basic.meta(), indent=2, ensure_ascii=False))

    def sql_query(self):
        print(self.api._stock_basic.sql("select list_status,count(*) cnt from {table}  group by list_status"))

    def xueqiu_query(self):
        xueqiu = tt.Tutake("../config.yml").xueqiu_api()
        # print(xueqiu.hot_stock(limit=10000))
        # print(xueqiu.index_valuation())


if __name__ == '__main__':
    test = Test()
    test.meta_query()
    test.sql_query()
    test.xueqiu_query()
