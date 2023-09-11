import pandas as pd
import pendulum

import tutake as tt
from tutake.api.ts.adj_factor import AdjFactor
from tutake.api.ts.monthly import Monthly
from tutake.api.ts.weekly import Weekly

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)  # 显示列数
    pd.set_option('display.width', 100)
    tutake = tt.Tutake("./config.yml")
    date = '20200102'
    ts_code = '000043.SZ'


    def prepare_ext(self):
        print(f"delete {ts_code}")
        session = self.session_factory()
        # session.query(self.entities).filter_by(trade_date=date).delete()
        session.query(self.entities).filter_by(ts_code=ts_code).delete()
        session.commit()


    def query_parameters_ext(self):
        # return [{"trade_date": date}]
        return [{"ts_code": ts_code}]
        # return [{}]


    def param_loop_process_ext(self, **params):
        return params


    api = AdjFactor(tutake.config)

    setattr(AdjFactor, 'prepare', prepare_ext)
    setattr(AdjFactor, 'query_parameters', query_parameters_ext)
    setattr(AdjFactor, 'param_loop_process', param_loop_process_ext)

    # api = Weekly(tutake.config)
    #
    # setattr(Weekly, 'prepare', prepare_ext)
    # setattr(Weekly, 'query_parameters', query_parameters_ext)
    # setattr(Weekly, 'param_loop_process', param_loop_process_ext)

    # api.process()  # 同步增量数据

    ts_codes = ['430017.BJ', '430047.BJ', '430090.BJ', '430139.BJ', '430198.BJ', '430300.BJ', '430418.BJ', '430425.BJ', '430476.BJ', '430478.BJ', '430489.BJ', '430510.BJ', '430556.BJ', '430564.BJ', '430685.BJ', '430718.BJ', '830779.BJ', '830799.BJ', '830809.BJ', '830832.BJ', '830839.BJ', '830879.BJ', '830896.BJ', '830946.BJ', '830964.BJ', '830974.BJ', '831010.BJ', '831039.BJ', '831087.BJ', '831152.BJ', '831167.BJ', '831195.BJ', '831278.BJ', '831304.BJ', '831305.BJ', '831370.BJ', '831445.BJ', '831526.BJ', '831627.BJ', '831641.BJ', '831689.BJ', '831726.BJ', '831768.BJ', '831832.BJ', '831834.BJ', '831855.BJ', '831856.BJ', '831906.BJ', '831961.BJ', '832000.BJ', '832023.BJ', '832089.BJ', '832110.BJ', '832145.BJ', '832149.BJ', '832171.BJ', '832175.BJ', '832225.BJ', '832278.BJ', '832317.BJ', '832419.BJ', '832471.BJ', '832491.BJ', '832566.BJ', '832651.BJ', '832662.BJ', '832735.BJ', '832802.BJ', '832876.BJ', '832885.BJ', '832982.BJ', '833075.BJ', '833171.BJ', '833230.BJ', '833266.BJ', '833346.BJ', '833394.BJ', '833427.BJ', '833429.BJ', '833454.BJ', '833455.BJ', '833509.BJ', '833523.BJ', '833533.BJ', '833575.BJ', '833580.BJ', '833751.BJ', '833781.BJ', '833819.BJ', '833873.BJ', '833874.BJ', '833914.BJ', '833943.BJ', '833994.BJ', '834014.BJ', '834021.BJ', '834033.BJ', '834058.BJ', '834062.BJ', '834261.BJ', '834407.BJ', '834415.BJ', '834475.BJ', '834599.BJ', '834639.BJ', '834682.BJ', '834765.BJ', '834770.BJ', '834950.BJ', '835174.BJ', '835179.BJ', '835184.BJ', '835185.BJ', '835207.BJ', '835237.BJ', '835305.BJ', '835368.BJ', '835508.BJ', '835640.BJ', '835670.BJ', '835857.BJ', '835892.BJ', '835985.BJ', '836077.BJ', '836149.BJ', '836208.BJ', '836221.BJ', '836239.BJ', '836247.BJ', '836260.BJ', '836263.BJ', '836270.BJ', '836395.BJ', '836414.BJ', '836422.BJ', '836433.BJ', '836504.BJ', '836675.BJ', '836699.BJ', '836717.BJ', '836720.BJ', '836807.BJ', '836826.BJ', '836871.BJ', '836892.BJ', '836942.BJ', '836957.BJ', '837006.BJ', '837046.BJ', '837092.BJ', '837174.BJ', '837212.BJ', '837242.BJ', '837344.BJ', '837592.BJ', '837663.BJ', '837748.BJ', '837821.BJ', '838030.BJ', '838163.BJ', '838171.BJ', '838227.BJ', '838262.BJ', '838275.BJ', '838402.BJ', '838670.BJ', '838701.BJ', '838810.BJ', '838837.BJ', '838924.BJ', '838971.BJ', '839167.BJ', '839273.BJ', '839371.BJ', '839680.BJ', '839719.BJ', '839725.BJ', '839729.BJ', '839790.BJ', '839792.BJ', '839946.BJ', '870199.BJ', '870204.BJ', '870299.BJ', '870357.BJ', '870436.BJ', '870508.BJ', '870726.BJ', '870866.BJ', '870976.BJ', '871245.BJ', '871396.BJ', '871478.BJ', '871553.BJ', '871634.BJ', '871642.BJ', '871694.BJ', '871753.BJ', '871857.BJ', '871970.BJ', '871981.BJ', '872190.BJ', '872351.BJ', '872374.BJ', '872392.BJ', '872541.BJ', '872808.BJ', '872895.BJ', '872925.BJ', '872953.BJ', '873001.BJ', '873122.BJ', '873152.BJ', '873167.BJ', '873169.BJ', '873223.BJ', '873305.BJ', '873339.BJ', '873527.BJ', '873576.BJ', '873593.BJ']


    # start = pendulum.parse(date)
    for i in ts_codes:
        ts_code = i
        api.process()  # 同步增量数据
        # start = start.add(days=1)
        # date = start.format('YYYYMMDD')

    # print(api.monthly(trade_date=date))  # 数据查询接口
