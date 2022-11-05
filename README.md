# Tutake

Take data from Tushare, respect Tushare!

自动生成代码，将Tushare的数据同步到本地，并同时保留Tushare的API进行本地数据的读取

### 背景

>最近发现量化是件有趣的事情，但相关数据的采集是件颇为棘手的事情，幸亏有Tushare， 可发现需要进行全市场的回测远程的接口性能还是有点弱，所以思考如何把数据存储到本地

### 实现

> 因为Tushare api及doc完整度非常高，就有了本项目的想法和实践--基于Tushare的api doc自动化的生成Tushare数据的全量同步及增量更新的代码，复用Tushare接口查询本地数据

#### Sample
数据的同步基本分为`历史数据`和`增量数据`处理两种场景，执行也很简单，以  `Tushare stock_basic`接口为例：
对应接口介绍 数据接口-沪深股票-基础数据-股票列表  https://tushare.pro/document/2?doc_id=25

自动生成的代码是 `stock_basic.py`
在main函数中能看到默认生成的代码：
```python
if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    api = StockBasic()
    api.process(ProcessType.HISTORY)  # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.stock_basic())  # 数据查询接口
```
执行后的结果：
```python
        ts_code  symbol  name  area  ... list_status list_date delist_date is_hs
0     000001.SZ  000001  平安银行    深圳  ...           L  19910403        None     S
1     000002.SZ  000002   万科A    深圳  ...           L  19910129        None     S
2     000004.SZ  000004  ST国华    深圳  ...           L  19910114        None     N
3     000005.SZ  000005  ST星源    深圳  ...           L  19901210        None     N
4     000006.SZ  000006  深振业A    深圳  ...           L  19920427        None     N
...         ...     ...   ...   ...  ...         ...       ...         ...   ...
4972  872925.BJ  872925  锦好医疗  None  ...           L  20211025        None     N
4973  873122.BJ  873122   中纺标  None  ...           L  20220927        None     N
4974  873169.BJ  873169  七丰精工  None  ...           L  20220415        None     N
4975  873223.BJ  873223  荣亿精密  None  ...           L  20220609        None     N
4976  873527.BJ  873527   夜光明  None  ...           L  20221027        None     N

[4977 rows x 15 columns]

```
***
再以`Tushare daily`接口为例:
```python
# 数据接口-沪深股票-行情数据-日线行情  https://tushare.pro/document/2?doc_id=27
if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    api = Daily()
    api.process(ProcessType.HISTORY)  # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.daily())  # 数据查询接口

```
这样就开始下载并导入A股历史的日K数据（可能需要花几个小时的时间，1G多的数据，还没做性能优化），务必要求 `StockBasic`的   `api.process(ProcessType.HISTORY)`已经成功执行，显示结果：
```python
            id    ts_code trade_date  ...  pct_chg         vol       amount
0     12412042  000001.SZ   20221104  ...   3.6398  1776112.23  1903720.944
1     12412043  000002.SZ   20221104  ...   2.9326  1077514.38  1500447.963
2     12412044  000004.SZ   20221104  ...   1.1416    11770.00    10392.991
3     12412045  000005.SZ   20221104  ...   1.1834    78672.00    13352.921
4     12412046  000006.SZ   20221104  ...   2.1390    89775.00    34065.087
...        ...        ...        ...  ...      ...         ...          ...
5995      4108  002368.SZ   20221102  ...  -1.0601   314414.13   873025.365
5996      4107  002369.SZ   20221102  ...   2.3454   343787.09   164993.228
5997      4106  002370.SZ   20221102  ...   0.5825   534621.43   277528.784
5998      4105  002371.SZ   20221102  ...  -1.2343    76915.84  2022068.928
5999      4104  002372.SZ   20221102  ...   1.3022   107220.93   201927.556

[6000 rows x 12 columns]
```

***
### 注意

执行其他api前，务必先执行 `stock_basic.py` 中的 `api.process(ProcessType.HISTORY)` 这样就有了所有的股票列表，这个数据是很多其他接口抓取数据的基础

### 项目结构

```
tutake
|- data 目前用sqlite保存，保存数据的目录
|- meta 保存TushareApi及相关配置的目录，目前也是用sqlite
|- tutake
    |- api 自动生成的代码，实现抓取数据并保存到数据库的能力
    |- code 采取TushareApi信息并根据模板生成api代码的
    |- util 部分工具代码
|- config-default.yml 配置文件模板，使用前需要把文件复制为config.yml才有效
```

### 已支持接口
目前调试测试的接口:
<a href="tutake/api/tushare">tutake/api/tushare</a>


### 替代Tushare使用
Tutake的接口和Tushare完全保持一致，同时也支持failover到Tushare，具体可以看测试代码：
<a href="test/test.py">test.py</a>

```python
import tutake as ts

if __name__ == '__main__':
    # 代码可以完全不用修改，只需要将import tushare改成tutake
    pro = ts.pro_api()
    print(pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date'))
    print(pro.stock_basic(limit=100))

    # 如果增加tushare_token 则支持使用Tushare进行Failover，未实现的函数依然调用tushare
    pro = ts.pro_api("tushare_token")   
    print(pro.shibor())
```


### 说明

目前项目处于比较早期的阶段，虽然代码能自动生成,但也有一定的差异的需要逐个调整配置，还需要花一些时间
此外因为刚学的python，很多语法、工程和最佳实践都还懵懂中，这个项目也算是python学习的项目
项目的易用性和完整度也很弱（多线程性能不提，定时任务、api配置管理刚需还没搞定），慢慢完善吧

当然最重要的一点是，我Tushare账号积分只有120个，很多接口限制没法调试，如果有人能借用就最好了:）

https://tushare.pro/register?reg=548467 没注册的用这个链接注册吧，我能赚点积分
