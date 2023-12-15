import os

import duckdb
from pathlib import Path

import tutake as tt


def load_data():
    dir = "database"
    con = duckdb.connect(str(Path(dir,'tutake.duckdb')))
    datas = {}
    for i, j, k in os.walk(dir):
        for file in k:
            if file.endswith('.parquet'):
                table = os.path.splitext(os.path.basename(file))[0]
                tokens = table.split("-")
                name = tokens[0]
                files = datas.get(name)
                if files is None:
                    files = []
                    datas[name] = files
                files.append(str(Path(dir,file)))
    for name, files in datas.items():
        con.execute(f"DROP TABLE IF EXISTS {name};")
        for file in files:
            if file == files[0]:
                print(f"Create {name} with {file}")
                con.execute(f"CREATE TABLE {name} AS SELECT * FROM read_parquet('{file}');")
            else:
                print(f"COPY {name} with {file}")
                con.execute(f"COPY {name} FROM '{file}' (FORMAT PARQUET);")
        con.execute("FORCE CHECKPOINT;")
    con.close()

def quick_start():
    tushare = tt.Tutake().tushare_api()
    # tutake = tt.Tutake("./config.yml")
    print("========查询股票数据========")
    print(tushare.stock_basic())
    print(tushare.daily())
    print(tushare.adj_factor())
    print(tushare.pro_bar(ts_code='000002.SZ', adj='hfq'))
    print(tushare._daily.sql("select * from {table} where trade_date='20221230' and close>open limit 5"))

def export():
    tutake = tt.Tutake("./config.yml").tushare_api()
    daily = tutake._daily
    daily.export("trade_date<'20000101'",'1990~1999')
    daily.export("trade_date>='20000101' and trade_date<'20100101'",'2000~2009')
    daily.export("trade_date>='20100101' and trade_date<'20200101'",'2010~2019')
    daily.export("trade_date>='20200101' and trade_date<'20230101'",'2020~2022')
    daily.export("trade_date>='20230101' and trade_date<'20240101'",'2023~')

    tutake._stock_basic.export()
    tutake._adj_factor.export()


def complete():
    tutake = tt.Tutake("./config.yml")
    # 通过以下的方式进行数据的同步，两种方式均可以同步数据
    tutake.process_api().daily()  # 单个接口的数据同步
    tutake.task_api().start(True)  # 启动全量的数据同步任务

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


def cron_task():
    tutake = tt.Tutake("./config.yml")
    tutake.task_api().start(True)  # 启动全量的数据同步任务


if __name__ == '__main__':
    # 加载数据,这个会将database中的数据生成数据库文件，执行一次即可，或者database中的数据有更新的再执行即可
    load_data()
    quick_start()

    # 全量的演示代码都在complete接口，但这个接口数据量很大，耗时很长，可以先尝试前面的小数据量的接口
    # complete()

    # 正式部署使用时，用这个接口
    # cron_task()
