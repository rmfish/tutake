
def say_hello_ext(self):
    print("Hello world! {}".format(self.name))


# if __name__ == '__main__':
    # 代码可以完全不用修改，只需要将import tushare改成tutake
    # pro = ts.pro_api()
    # print(pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date'))
    # print(pro.stock_basic(limit=100))
    #
    # # 如果增加tushare_token 则支持使用Tushare进行Failover，未实现的函数依然调用tushare
    # pro = ts.pro_api("tushare_token")
    # print(pro.shibor())

    # a = A()
    # a.say_hello()
