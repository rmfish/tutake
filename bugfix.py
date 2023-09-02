import pandas as pd

import tutake as tt
from tutake.api.ts.adj_factor import AdjFactor
from tutake.api.ts.monthly import Monthly

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)  # 显示列数
    pd.set_option('display.width', 100)
    tutake = tt.Tutake("./config.yml")


    def prepare_ext(self):
        session = self.session_factory()
        session.query(self.entities).filter_by(ts_code='689009.SH').delete()
        session.commit()


    def query_parameters_ext(self):
        return [{"ts_code": '689009.SH'}]
        # return [{}]


    def param_loop_process_ext(self, **params):
        return params


    api = AdjFactor(tutake.config)

    setattr(AdjFactor, 'prepare', prepare_ext)
    setattr(AdjFactor, 'query_parameters', query_parameters_ext)
    setattr(AdjFactor, 'param_loop_process', param_loop_process_ext)

    api.process()  # 同步增量数据
    print(api.adj_factor(ts_code='689009.SH'))  # 数据查询接口
