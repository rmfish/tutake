# Tutake

Take data from Tushare, respect Tushare!

自动生成代码，将Tushare的数据同步到本地，并同时保留Tushare的API进行本地数据的读取

## 背景

> 最近发现量化是件有趣的事情，但相关数据的采集是件颇为棘手的事情，幸亏有Tushare， 可发现需要进行全市场的回测远程的接口性能还是有点弱，所以思考如何把数据存储到本地

## 实现

> 因为Tushare api及doc完整度非常高，就有了本项目的想法和实践--基于Tushare的api
> doc自动化的生成Tushare数据的全量同步及增量更新的代码，复用Tushare接口查询本地数据

## 使用

### Step1 设置配置文件

clone 代码后复制配置文件 `config-default.yml` -> `config.yml`
需要配置两个参数：

```yaml
#执行时需要将这个文件调整为 config.yml
tutake:
  data:
    driver_url: sqlite:////Users/xxx/tutake/data  # sqlite的driver的地址，制定到存放下载数据的目录，注意不同操作系统的/可能会有差异

tushare:
  token: # Tushare的token 尽量使用高积分的Token，否则会有很多接口和频率的限制
```

### Step2 下载股票列表

打开 <a href="tutake/api/tushare/stock_basic.py">tutake/api/tushare/stock_basic.py</a>
执行main函数，开始同步下载数据

```python
if __name__ == '__main__':
    api = StockBasic()
    api.process(ProcessType.HISTORY) 
```

执行完毕就可以从本地查询数据:

```python
if __name__ == '__main__':
    api = StockBasic()
    print(api.stock_basic())  # 数据查询接口
```
显示查询结果：
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

### Step3 下载股票日/周/月 数据

执行完上一步，即可开始下载常见的股票HLOC数据

> 日数据: <a href="tutake/api/tushare/daily.py">tutake/api/tushare/daily.py</a>
>
>周数据: <a href="tutake/api/tushare/weekly.py">tutake/api/tushare/weekly.py</a>
>
>月数据: <a href="tutake/api/tushare/monthly.py">tutake/api/tushare/monthly.py</a>

执行对应的main函数，开始同步下载数据，以日数据为例(日数据量比较大，需要一段时间下载)：

```python
if __name__ == '__main__':
    pd.set_option('display.max_columns', 500)  # 显示列数
    pd.set_option('display.width', 1000)
    logger.setLevel(logging.INFO)
    api = Daily()
    api.process(ProcessType.HISTORY)  # 同步历史数据
    # api.process(ProcessType.INCREASE)  # 同步增量数据
    print(api.daily())  # 数据查询接口
```

### StepN 执行其他接口
其他的接口也类似，可以在api代码中逐一执行尝试，有代码的接口基本都已经测试过，有问题可以随时反馈，其他接口陆续增加，也欢迎大家参与接口的调试和配置

## 只作为客户端使用

如果数据下载完成后，只做客户端使用，和Tushare的接口完全保持一致，如果设置Tushare的Token，还支持接口的降级（未实现的接口直接调用Tushare）
```python
import tutake as ts

if __name__ == '__main__':
    pro = ts.pro_api(token="xxxxxx")  #token可以不配置，只有在需要failover时使用
    print(pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date'))
    print(pro.stock_basic(limit=100))
```

## 说明

目前项目处于比较早期的阶段，虽然代码能自动生成,但也有一定的差异的需要逐个调整配置，还需要花一些时间
此外因为刚学的python，很多语法、工程和最佳实践都还懵懂中，这个项目也算是python学习的项目
项目的易用性和完整度不足（定时任务），慢慢完善吧，欢迎大家共建

## 关于数据
基本一个接口会有一个数据文件，但是数据文件会比较大，如果有人想直接要这个数据，也可以加Star留言

![data.png](data.png)


当然最重要的一点是，我Tushare账号积分只有120个，很多接口限制没法调试:）

https://tushare.pro/register?reg=548467 没注册的用这个链接注册吧，我能赚点积分
