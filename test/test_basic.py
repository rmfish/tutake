import quantstats as qs
import yfinance as _yf

import tutake as ts

if __name__ == '__main__':
    pro = ts.pro_api()
    qs.extend_pandas()
    stock = qs.utils.download_returns('BABA', "http://127.0.0.1:6152")
    qs.stats.sharpe(stock)

    # or using extend_pandas() :)
    print(stock.sharpe())
    # print(_yf.Ticker('BABA').history(**{"period": "max", "proxy": "http://127.0.0.1:6152"}))

    # print(stock)
    # stock.plot_snapshot(title='Facebook Performance')
    # qs.reports.metrics(stock, "SPY", output='test.html')
    # qs.plots.snapshot(pro.daily(ts_code='000001.SZ'), "000001.SZ")
    # print(pro.daily())
    # print(pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date'))
    # print(pro.stock_basic(limit=100))
