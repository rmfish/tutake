import tutake as ts

if __name__ == '__main__':
    pro = ts.pro_api(token="xxxxxx")
    print(pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date'))
    print(pro.stock_basic(limit=100))
