import tutake as tt

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")

    # 通过以下的方式进行数据的同步，两种方式均可以同步数据
    tutake.task_api().start(True)  # 启动全量的数据同步任务
    tutake.process_api().daily()  # 单个接口的数据同步

    # 通过以下的方式进行数据的查询
    ts_api = tutake.tushare_api()
    print(ts_api.apis())  # 所有支持的api
    print(ts_api.daily(ts_code='000002.SZ'))  # 查询000002.SZ每日数据
    print(ts_api.pro_bar(ts_code='000002.SZ', adj='hfq'))  # 查询000002.SZ的后复权数据
    print(ts_api._daily.sql("select * from {table} where trade_date='20221230' and close>open limit 5"))  # 通过sql直接查询数据
    print(ts_api._daily.meta())  # 查看接口元数据

    xq_api = tutake.xueqiu_api()
    print(xq_api.apis())  # 雪球所有支持的api
    print(xq_api.index_valuation())  # 指数的每日估值
    print(xq_api._index_valuation.meta())  # 指数的每日估值元数据
