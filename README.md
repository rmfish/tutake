# Tutake

Take data from Tushare, respect Tushare!

1. 支持定时自动化的下载tushare数据，保证数据的同步
2. 支持本地的数据查询，性能和效率更高（当前使用sqlite,后续计划支持多类型数据库）
3. 支持原生的查询，分析的维度更灵活（sql还是很强大的）
4. 支持接口的扩展，常用的数据组合接口可以通过扩展的方式统一调用(目前增加了雪球热榜的接口)

## 背景

> 最近发现量化是件有趣的事情，但相关数据的采集是件颇为棘手的事情，幸亏有Tushare， 可发现需要进行全市场的回测远程的接口性能还是有点弱，所以思考如何把数据存储到本地

## 实现

> 因为Tushare api及doc完整度非常高，就有了本项目的想法和实践--基于Tushare的api
> doc自动化的生成Tushare数据的全量同步及增量更新的代码，复用Tushare接口查询本地数据，同时支持定时执行数据同步。

## 使用

### Step1 设置配置文件

clone 代码后复制配置文件 `config-default.yml` -> `config.yml`
需要配置两个参数：

```yaml
#执行时需要将这个文件复制为 config.yml
tutake:
  data:
    dir: ~/.tutake/data  #单独指定数据的目录
  scheduler:
    tasks:
      - default: 10 0,11,21 * * *
      - stock_basic: 0 0,11,21 * * *

tushare:
  token: #tushare api 的token，如果需要获取所有的数据，需要5000以上的积分
```

具体的api的使用，可以直接参考代码 <a href="main.py">main.py</a>

### Step2 下载股票列表
执行main函数，开始同步下载数据

```python
import tutake as tt

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")

    # 通过以下的方式进行数据的同步，两种方式均可以同步数据
    tutake.task_api().start(True)  # 启动全量的数据同步任务
    tutake.process_api().daily()  # 单个接口的数据同步
```

### Step3 查询数据
下载完数据就可以从本地查询数据:

```python
import tutake as tt

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")
    # 通过以下的方式进行数据的查询
    ts_api = tutake.tushare_api()
    print(ts_api.apis())  # 所有支持的api
```
显示支持的apis：
```python
['adj_factor', 'stock_company', 'daily', 'moneyflow', 'bak_daily', 'namechange', 'fund_basic', 'monthly', 'moneyflow_hsgt', 'stk_rewards', 'hs_const', 'bak_basic', 'suspend_d', 'weekly', 'stock_basic', 'new_share', 'stk_managers', 'daily_basic', 'ggt_daily', 'ggt_top10', 'hsgt_top10', 'ggt_monthly', 'income_vip', 'balancesheet_vip', 'cashflow_vip', 'forecast_vip', 'express_vip', 'dividend', 'fina_indicator_vip', 'ths_daily', 'ths_member', 'anns', 'trade_cal', 'fund_adj', 'fund_company', 'fund_div', 'fund_manager', 'fund_nav', 'fund_portfolio', 'fund_sales_ratio', 'fund_sales_vol', 'fund_share', 'fund_daily', 'index_basic', 'index_daily', 'index_dailybasic', 'index_classify', 'index_member', 'ths_index', 'index_global', 'daily_full']
```

查询000002.SZ的daily数据：
```python
import tutake as tt

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")
    # 通过以下的方式进行数据的查询
    ts_api = tutake.tushare_api()
    print(ts_api.daily(ts_code='000002.SZ'))  # 查询000002.SZ每日数据
```

```python
        ts_code trade_date   open  ...  pct_chg         vol        amount
0     000002.SZ   19910129  14.58  ...  1358.00        3.00  2.200000e+01
1     000002.SZ   19910130  14.51  ...    -0.48       17.00  1.230000e+02
2     000002.SZ   19910204  14.66  ...     0.48       56.00  4.100000e+02
3     000002.SZ   19910205  14.73  ...     0.48       29.00  2.130000e+02
4     000002.SZ   19910206  14.80  ...     0.48       29.00  2.150000e+02
...         ...        ...    ...  ...      ...         ...           ...
5995  000002.SZ   20160824  24.40  ...    -2.87  1470675.59  3.561540e+06
5996  000002.SZ   20160825  23.50  ...    -1.88  1821374.91  4.234199e+06
5997  000002.SZ   20160826  23.59  ...    -2.76  1200024.09  2.780659e+06
5998  000002.SZ   20160829  22.86  ...     0.09   782446.19  1.796321e+06
5999  000002.SZ   20160830  22.95  ...    -1.09   909262.53  2.072873e+06

[6000 rows x 11 columns]
```

使用pro_bar接口获取更复杂的数据，例如获得000002.SZ的后复权数据：
```python
import tutake as tt

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")
    # 通过以下的方式进行数据的查询
    ts_api = tutake.tushare_api()
    print(ts_api.pro_bar(ts_code='000002.SZ', adj='hfq'))  # 查询000002.SZ的后复权数据
```
```python
        ts_code trade_date       open  ...    pct_chg         vol        amount
0     000002.SZ   19910129   100.5728  ...  1357.9994        3.00  2.200000e+01
1     000002.SZ   19910130   100.0900  ...    -0.4801       17.00  1.230000e+02
2     000002.SZ   19910204   101.1247  ...     0.4798       56.00  4.100000e+02
3     000002.SZ   19910205   101.6075  ...     0.4774       29.00  2.130000e+02
4     000002.SZ   19910206   102.0904  ...     0.4753       29.00  2.150000e+02
...         ...        ...        ...  ...        ...         ...           ...
5995  000002.SZ   20160824  3239.8808  ...    -2.8745  1470675.59  3.561540e+06
5996  000002.SZ   20160825  3120.3770  ...    -1.8758  1821374.91  4.234199e+06
5997  000002.SZ   20160826  3132.3274  ...    -2.7613  1200024.09  2.780659e+06
5998  000002.SZ   20160829  3035.3965  ...     0.0874   782446.19  1.796321e+06
5999  000002.SZ   20160830  3047.3469  ...    -1.0912   909262.53  2.072873e+06

[6000 rows x 11 columns]
```

原生sql查询

一些特殊场景下需要需要更多维度的查询，所以也支持使用sql查询。
只需要通过接口前加上_就可以，比如股票日数据`daily`接口可以用`_daily`来访问
```python
import tutake as tt

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")
    # 通过以下的方式进行数据的查询
    ts_api = tutake.tushare_api()
    print(ts_api._daily.sql("select * from {table} where trade_date='20221230' and close>open limit 5"))  # 通过sql直接查询数据
```
```python
    ts_code trade_date  open  high  ...  change  pct_chg        vol      amount
0  002198.SZ   20221230  6.39  6.57  ...    0.12   1.8750  101579.12   65646.164
1  002199.SZ   20221230  6.36  6.43  ...    0.10   1.5898   38684.00   24640.014
2  002194.SZ   20221230  9.13  9.26  ...    0.11   1.2088  101101.41   92895.425
3  002181.SZ   20221230  5.28  5.52  ...    0.15   2.8249  547665.70  297495.407
4  002195.SZ   20221230  1.99  2.02  ...    0.03   1.5152  444728.72   89088.620

[5 rows x 11 columns]
```

也可以查看接口的元数据：
```python
import tutake as tt

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")
    # 通过以下的方式进行数据的查询
    ts_api = tutake.tushare_api()
    print(ts_api._daily.meta())  # 查看接口元数据
```
结果如下：
```json lines
{'table_name': 'tushare_daily', 'columns': [{'name': 'ts_code', 'type': 'String', 'comment': '股票代码'}, {'name': 'trade_date', 'type': 'String', 'comment': '交易日期'}, {'name': 'open', 'type': 'Float', 'comment': '开盘价'}, {'name': 'high', 'type': 'Float', 'comment': '最高价'}, {'name': 'low', 'type': 'Float', 'comment': '最低价'}, {'name': 'close', 'type': 'Float', 'comment': '收盘价'}, {'name': 'pre_close', 'type': 'Float', 'comment': '昨收价'}, {'name': 'change', 'type': 'Float', 'comment': '涨跌额'}, {'name': 'pct_chg', 'type': 'Float', 'comment': '涨跌幅'}, {'name': 'vol', 'type': 'Float', 'comment': '成交量'}, {'name': 'amount', 'type': 'Float', 'comment': '成交额'}], 'default_order_by': 'trade_date,ts_code', 'default_limit': '6000'}
```

而外还有雪球的一些接口支持：
```python
import tutake as tt

if __name__ == '__main__':
    tutake = tt.Tutake("./config.yml")

    xq_api = tutake.xueqiu_api()
    print(xq_api.apis())  # 雪球所有支持的api
    print(xq_api.index_valuation())  # 指数的每日估值
    print(xq_api._index_valuation.meta())  # 指数的每日估值元数据

```
```python
    ts_code trade_date  open  high  ...  change  pct_chg        vol      amount
0  002198.SZ   20221230  6.39  6.57  ...    0.12   1.8750  101579.12   65646.164
1  002199.SZ   20221230  6.36  6.43  ...    0.10   1.5898   38684.00   24640.014
2  002194.SZ   20221230  9.13  9.26  ...    0.11   1.2088  101101.41   92895.425
3  002181.SZ   20221230  5.28  5.52  ...    0.15   2.8249  547665.70  297495.407
4  002195.SZ   20221230  1.99  2.02  ...    0.03   1.5152  444728.72   89088.620

[5 rows x 11 columns]
```

## 说明
因为数据量比较大，全量的数据超过百G，但是tushare有限速限量的各种约束，所以建议使用多个高等级的账号（5000积分以上的账号），工程支持配置多个账号，然后自动适配限流下载，全量数据下载完后，每天的增量数据量很小，通常10分钟内下载完毕，
目前调试的接口是按照个人需要生成的，还有很多接口没有生成，如果有需要的可以留言，或者阅读代码自行添加。目前的接口基本覆盖了股票、基金、指数、期货相关的接口

## 关于数据
基本一个接口会有一个数据文件，但是数据文件会比较大，如果有人想直接要这个数据，也可以加Star留言，后续数据稳定了，会发布历史数据供大家一次性下载。同时也计划开发定期增量数据更新的功能(日/周/月/季度/年)，解决大家账号低权限无法下载的问题。

![data.png](data.png)


## 计划
目前距离生产可用性的距离还很远，但是希望能不断优化接近高可用，当然还有更多的功能也会不断增加
