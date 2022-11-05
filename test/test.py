import tutake as tt

if __name__ == '__main__':
    pro = tt.pro_api()
    print(pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date'))
    print(pro.stock_basic(limit=100))
