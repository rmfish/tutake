"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fina_indicator_vip接口
获取上市公司财务指标数据
数据接口-沪深股票-财务数据-财务指标数据  https://tushare.pro/document/2?doc_id=7900

@author: rmfish
"""
import pandas as pd
from sqlalchemy import Integer, String, Float, Column
from sqlalchemy.orm import sessionmaker

from tutake.api.base_dao import BaseDao, BatchWriter, TutakeTableBase
from tutake.api.process import DataProcess, ProcessException
from tutake.api.ts import fina_indicator_vip_ext
from tutake.api.ts.tushare_dao import TushareDAO, create_shared_engine
from tutake.api.ts.tushare_api import TushareAPI
from tutake.api.ts.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.decorator import extends_attr
from tutake.utils.utils import project_root


class TushareFinaIndicatorVip(TutakeTableBase):
    __tablename__ = "tushare_fina_indicator_vip"
    ts_code = Column(String, index=True, comment='TS代码')
    ann_date = Column(String, index=True, comment='公告日期')
    end_date = Column(String, index=True, comment='报告期')
    eps = Column(Float, comment='基本每股收益')
    dt_eps = Column(Float, comment='稀释每股收益')
    total_revenue_ps = Column(Float, comment='每股营业总收入')
    revenue_ps = Column(Float, comment='每股营业收入')
    capital_rese_ps = Column(Float, comment='每股资本公积')
    surplus_rese_ps = Column(Float, comment='每股盈余公积')
    undist_profit_ps = Column(Float, comment='每股未分配利润')
    extra_item = Column(Float, comment='非经常性损益')
    profit_dedt = Column(Float, comment='扣除非经常性损益后的净利润')
    gross_margin = Column(Float, comment='毛利')
    current_ratio = Column(Float, comment='流动比率')
    quick_ratio = Column(Float, comment='速动比率')
    cash_ratio = Column(Float, comment='保守速动比率')
    invturn_days = Column(Float, comment='存货周转天数')
    arturn_days = Column(Float, comment='应收账款周转天数')
    inv_turn = Column(Float, comment='存货周转率')
    ar_turn = Column(Float, comment='应收账款周转率')
    ca_turn = Column(Float, comment='流动资产周转率')
    fa_turn = Column(Float, comment='固定资产周转率')
    assets_turn = Column(Float, comment='总资产周转率')
    op_income = Column(Float, comment='经营活动净收益')
    valuechange_income = Column(Float, comment='价值变动净收益')
    interst_income = Column(Float, comment='利息费用')
    daa = Column(Float, comment='折旧与摊销')
    ebit = Column(Float, comment='息税前利润')
    ebitda = Column(Float, comment='息税折旧摊销前利润')
    fcff = Column(Float, comment='企业自由现金流量')
    fcfe = Column(Float, comment='股权自由现金流量')
    current_exint = Column(Float, comment='无息流动负债')
    noncurrent_exint = Column(Float, comment='无息非流动负债')
    interestdebt = Column(Float, comment='带息债务')
    netdebt = Column(Float, comment='净债务')
    tangible_asset = Column(Float, comment='有形资产')
    working_capital = Column(Float, comment='营运资金')
    networking_capital = Column(Float, comment='营运流动资本')
    invest_capital = Column(Float, comment='全部投入资本')
    retained_earnings = Column(Float, comment='留存收益')
    diluted2_eps = Column(Float, comment='期末摊薄每股收益')
    bps = Column(Float, comment='每股净资产')
    ocfps = Column(Float, comment='每股经营活动产生的现金流量净额')
    retainedps = Column(Float, comment='每股留存收益')
    cfps = Column(Float, comment='每股现金流量净额')
    ebit_ps = Column(Float, comment='每股息税前利润')
    fcff_ps = Column(Float, comment='每股企业自由现金流量')
    fcfe_ps = Column(Float, comment='每股股东自由现金流量')
    netprofit_margin = Column(Float, comment='销售净利率')
    grossprofit_margin = Column(Float, comment='销售毛利率')
    cogs_of_sales = Column(Float, comment='销售成本率')
    expense_of_sales = Column(Float, comment='销售期间费用率')
    profit_to_gr = Column(Float, comment='净利润/营业总收入')
    saleexp_to_gr = Column(Float, comment='销售费用/营业总收入')
    adminexp_of_gr = Column(Float, comment='管理费用/营业总收入')
    finaexp_of_gr = Column(Float, comment='财务费用/营业总收入')
    impai_ttm = Column(Float, comment='资产减值损失/营业总收入')
    gc_of_gr = Column(Float, comment='营业总成本/营业总收入')
    op_of_gr = Column(Float, comment='营业利润/营业总收入')
    ebit_of_gr = Column(Float, comment='息税前利润/营业总收入')
    roe = Column(Float, comment='净资产收益率')
    roe_waa = Column(Float, comment='加权平均净资产收益率')
    roe_dt = Column(Float, comment='净资产收益率(扣除非经常损益)')
    roa = Column(Float, comment='总资产报酬率')
    npta = Column(Float, comment='总资产净利润')
    roic = Column(Float, comment='投入资本回报率')
    roe_yearly = Column(Float, comment='年化净资产收益率')
    roa2_yearly = Column(Float, comment='年化总资产报酬率')
    roe_avg = Column(Float, comment='平均净资产收益率(增发条件)')
    opincome_of_ebt = Column(Float, comment='经营活动净收益/利润总额')
    investincome_of_ebt = Column(Float, comment='价值变动净收益/利润总额')
    n_op_profit_of_ebt = Column(Float, comment='营业外收支净额/利润总额')
    tax_to_ebt = Column(Float, comment='所得税/利润总额')
    dtprofit_to_profit = Column(Float, comment='扣除非经常损益后的净利润/净利润')
    salescash_to_or = Column(Float, comment='销售商品提供劳务收到的现金/营业收入')
    ocf_to_or = Column(Float, comment='经营活动产生的现金流量净额/营业收入')
    ocf_to_opincome = Column(Float, comment='经营活动产生的现金流量净额/经营活动净收益')
    capitalized_to_da = Column(Float, comment='资本支出/折旧和摊销')
    debt_to_assets = Column(Float, comment='资产负债率')
    assets_to_eqt = Column(Float, comment='权益乘数')
    dp_assets_to_eqt = Column(Float, comment='权益乘数(杜邦分析)')
    ca_to_assets = Column(Float, comment='流动资产/总资产')
    nca_to_assets = Column(Float, comment='非流动资产/总资产')
    tbassets_to_totalassets = Column(Float, comment='有形资产/总资产')
    int_to_talcap = Column(Float, comment='带息债务/全部投入资本')
    eqt_to_talcapital = Column(Float, comment='归属于母公司的股东权益/全部投入资本')
    currentdebt_to_debt = Column(Float, comment='流动负债/负债合计')
    longdeb_to_debt = Column(Float, comment='非流动负债/负债合计')
    ocf_to_shortdebt = Column(Float, comment='经营活动产生的现金流量净额/流动负债')
    debt_to_eqt = Column(Float, comment='产权比率')
    eqt_to_debt = Column(Float, comment='归属于母公司的股东权益/负债合计')
    eqt_to_interestdebt = Column(Float, comment='归属于母公司的股东权益/带息债务')
    tangibleasset_to_debt = Column(Float, comment='有形资产/负债合计')
    tangasset_to_intdebt = Column(Float, comment='有形资产/带息债务')
    tangibleasset_to_netdebt = Column(Float, comment='有形资产/净债务')
    ocf_to_debt = Column(Float, comment='经营活动产生的现金流量净额/负债合计')
    ocf_to_interestdebt = Column(Float, comment='经营活动产生的现金流量净额/带息债务')
    ocf_to_netdebt = Column(Float, comment='经营活动产生的现金流量净额/净债务')
    ebit_to_interest = Column(Float, comment='已获利息倍数(EBIT/利息费用)')
    longdebt_to_workingcapital = Column(Float, comment='长期债务与营运资金比率')
    ebitda_to_debt = Column(Float, comment='息税折旧摊销前利润/负债合计')
    turn_days = Column(Float, comment='营业周期')
    roa_yearly = Column(Float, comment='年化总资产净利率')
    roa_dp = Column(Float, comment='总资产净利率(杜邦分析)')
    fixed_assets = Column(Float, comment='固定资产合计')
    profit_prefin_exp = Column(Float, comment='扣除财务费用前营业利润')
    non_op_profit = Column(Float, comment='非营业利润')
    op_to_ebt = Column(Float, comment='营业利润／利润总额')
    nop_to_ebt = Column(Float, comment='非营业利润／利润总额')
    ocf_to_profit = Column(Float, comment='经营活动产生的现金流量净额／营业利润')
    cash_to_liqdebt = Column(Float, comment='货币资金／流动负债')
    cash_to_liqdebt_withinterest = Column(Float, comment='货币资金／带息流动负债')
    op_to_liqdebt = Column(Float, comment='营业利润／流动负债')
    op_to_debt = Column(Float, comment='营业利润／负债合计')
    roic_yearly = Column(Float, comment='年化投入资本回报率')
    total_fa_trun = Column(Float, comment='固定资产合计周转率')
    profit_to_op = Column(Float, comment='利润总额／营业收入')
    q_opincome = Column(Float, comment='经营活动单季度净收益')
    q_investincome = Column(Float, comment='价值变动单季度净收益')
    q_dtprofit = Column(Float, comment='扣除非经常损益后的单季度净利润')
    q_eps = Column(Float, comment='每股收益(单季度)')
    q_netprofit_margin = Column(Float, comment='销售净利率(单季度)')
    q_gsprofit_margin = Column(Float, comment='销售毛利率(单季度)')
    q_exp_to_sales = Column(Float, comment='销售期间费用率(单季度)')
    q_profit_to_gr = Column(Float, comment='净利润／营业总收入(单季度)')
    q_saleexp_to_gr = Column(Float, comment='销售费用／营业总收入 (单季度)')
    q_adminexp_to_gr = Column(Float, comment='管理费用／营业总收入 (单季度)')
    q_finaexp_to_gr = Column(Float, comment='财务费用／营业总收入 (单季度)')
    q_impair_to_gr_ttm = Column(Float, comment='资产减值损失／营业总收入(单季度)')
    q_gc_to_gr = Column(Float, comment='营业总成本／营业总收入 (单季度)')
    q_op_to_gr = Column(Float, comment='营业利润／营业总收入(单季度)')
    q_roe = Column(Float, comment='净资产收益率(单季度)')
    q_dt_roe = Column(Float, comment='净资产单季度收益率(扣除非经常损益)')
    q_npta = Column(Float, comment='总资产净利润(单季度)')
    q_opincome_to_ebt = Column(Float, comment='经营活动净收益／利润总额(单季度)')
    q_investincome_to_ebt = Column(Float, comment='价值变动净收益／利润总额(单季度)')
    q_dtprofit_to_profit = Column(Float, comment='扣除非经常损益后的净利润／净利润(单季度)')
    q_salescash_to_or = Column(Float, comment='销售商品提供劳务收到的现金／营业收入(单季度)')
    q_ocf_to_sales = Column(Float, comment='经营活动产生的现金流量净额／营业收入(单季度)')
    q_ocf_to_or = Column(Float, comment='经营活动产生的现金流量净额／经营活动净收益(单季度)')
    basic_eps_yoy = Column(Float, comment='基本每股收益同比增长率(%)')
    dt_eps_yoy = Column(Float, comment='稀释每股收益同比增长率(%)')
    cfps_yoy = Column(Float, comment='每股经营活动产生的现金流量净额同比增长率(%)')
    op_yoy = Column(Float, comment='营业利润同比增长率(%)')
    ebt_yoy = Column(Float, comment='利润总额同比增长率(%)')
    netprofit_yoy = Column(Float, comment='归属母公司股东的净利润同比增长率(%)')
    dt_netprofit_yoy = Column(Float, comment='归属母公司股东的净利润-扣除非经常损益同比增长率(%)')
    ocf_yoy = Column(Float, comment='经营活动产生的现金流量净额同比增长率(%)')
    roe_yoy = Column(Float, comment='净资产收益率(摊薄)同比增长率(%)')
    bps_yoy = Column(Float, comment='每股净资产相对年初增长率(%)')
    assets_yoy = Column(Float, comment='资产总计相对年初增长率(%)')
    eqt_yoy = Column(Float, comment='归属母公司的股东权益相对年初增长率(%)')
    tr_yoy = Column(Float, comment='营业总收入同比增长率(%)')
    or_yoy = Column(Float, comment='营业收入同比增长率(%)')
    q_gr_yoy = Column(Float, comment='营业总收入同比增长率(%)(单季度)')
    q_gr_qoq = Column(Float, comment='营业总收入环比增长率(%)(单季度)')
    q_sales_yoy = Column(Float, comment='营业收入同比增长率(%)(单季度)')
    q_sales_qoq = Column(Float, comment='营业收入环比增长率(%)(单季度)')
    q_op_yoy = Column(Float, comment='营业利润同比增长率(%)(单季度)')
    q_op_qoq = Column(Float, comment='营业利润环比增长率(%)(单季度)')
    q_profit_yoy = Column(Float, comment='净利润同比增长率(%)(单季度)')
    q_profit_qoq = Column(Float, comment='净利润环比增长率(%)(单季度)')
    q_netprofit_yoy = Column(Float, comment='归属母公司股东的净利润同比增长率(%)(单季度)')
    q_netprofit_qoq = Column(Float, comment='归属母公司股东的净利润环比增长率(%)(单季度)')
    equity_yoy = Column(Float, comment='净资产同比增长率')
    rd_exp = Column(Float, comment='研发费用')
    update_flag = Column(String, index=True, comment='更新标识')


class FinaIndicatorVip(TushareDAO, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.table_name = "tushare_fina_indicator_vip"
        self.database = 'tutake.duckdb'
        self.database_dir = config.get_tutake_data_dir()
        self.database_url = config.get_data_driver_url(self.database)
        self.engine = create_shared_engine(self.database_url,
                                           connect_args={
                                               'check_same_thread': False,
                                               'timeout': config.get_sqlite_timeout()
                                           })
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareFinaIndicatorVip.__table__.create(bind=self.engine, checkfirst=True)
        self.schema = BaseDao.parquet_schema(TushareFinaIndicatorVip)

        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'period', 'update_flag', 'limit', 'offset']
        self.tushare_fields = [
            "ts_code", "ann_date", "end_date", "eps", "dt_eps", "total_revenue_ps", "revenue_ps", "capital_rese_ps",
            "surplus_rese_ps", "undist_profit_ps", "extra_item", "profit_dedt", "gross_margin", "current_ratio",
            "quick_ratio", "cash_ratio", "invturn_days", "arturn_days", "inv_turn", "ar_turn", "ca_turn", "fa_turn",
            "assets_turn", "op_income", "valuechange_income", "interst_income", "daa", "ebit", "ebitda", "fcff", "fcfe",
            "current_exint", "noncurrent_exint", "interestdebt", "netdebt", "tangible_asset", "working_capital",
            "networking_capital", "invest_capital", "retained_earnings", "diluted2_eps", "bps", "ocfps", "retainedps",
            "cfps", "ebit_ps", "fcff_ps", "fcfe_ps", "netprofit_margin", "grossprofit_margin", "cogs_of_sales",
            "expense_of_sales", "profit_to_gr", "saleexp_to_gr", "adminexp_of_gr", "finaexp_of_gr", "impai_ttm",
            "gc_of_gr", "op_of_gr", "ebit_of_gr", "roe", "roe_waa", "roe_dt", "roa", "npta", "roic", "roe_yearly",
            "roa2_yearly", "roe_avg", "opincome_of_ebt", "investincome_of_ebt", "n_op_profit_of_ebt", "tax_to_ebt",
            "dtprofit_to_profit", "salescash_to_or", "ocf_to_or", "ocf_to_opincome", "capitalized_to_da",
            "debt_to_assets", "assets_to_eqt", "dp_assets_to_eqt", "ca_to_assets", "nca_to_assets",
            "tbassets_to_totalassets", "int_to_talcap", "eqt_to_talcapital", "currentdebt_to_debt", "longdeb_to_debt",
            "ocf_to_shortdebt", "debt_to_eqt", "eqt_to_debt", "eqt_to_interestdebt", "tangibleasset_to_debt",
            "tangasset_to_intdebt", "tangibleasset_to_netdebt", "ocf_to_debt", "ocf_to_interestdebt", "ocf_to_netdebt",
            "ebit_to_interest", "longdebt_to_workingcapital", "ebitda_to_debt", "turn_days", "roa_yearly", "roa_dp",
            "fixed_assets", "profit_prefin_exp", "non_op_profit", "op_to_ebt", "nop_to_ebt", "ocf_to_profit",
            "cash_to_liqdebt", "cash_to_liqdebt_withinterest", "op_to_liqdebt", "op_to_debt", "roic_yearly",
            "total_fa_trun", "profit_to_op", "q_opincome", "q_investincome", "q_dtprofit", "q_eps",
            "q_netprofit_margin", "q_gsprofit_margin", "q_exp_to_sales", "q_profit_to_gr", "q_saleexp_to_gr",
            "q_adminexp_to_gr", "q_finaexp_to_gr", "q_impair_to_gr_ttm", "q_gc_to_gr", "q_op_to_gr", "q_roe",
            "q_dt_roe", "q_npta", "q_opincome_to_ebt", "q_investincome_to_ebt", "q_dtprofit_to_profit",
            "q_salescash_to_or", "q_ocf_to_sales", "q_ocf_to_or", "basic_eps_yoy", "dt_eps_yoy", "cfps_yoy", "op_yoy",
            "ebt_yoy", "netprofit_yoy", "dt_netprofit_yoy", "ocf_yoy", "roe_yoy", "bps_yoy", "assets_yoy", "eqt_yoy",
            "tr_yoy", "or_yoy", "q_gr_yoy", "q_gr_qoq", "q_sales_yoy", "q_sales_qoq", "q_op_yoy", "q_op_qoq",
            "q_profit_yoy", "q_profit_qoq", "q_netprofit_yoy", "q_netprofit_qoq", "equity_yoy", "rd_exp", "update_flag"
        ]
        entity_fields = [
            "ts_code", "ann_date", "end_date", "eps", "dt_eps", "total_revenue_ps", "revenue_ps", "capital_rese_ps",
            "surplus_rese_ps", "undist_profit_ps", "extra_item", "profit_dedt", "gross_margin", "current_ratio",
            "quick_ratio", "cash_ratio", "invturn_days", "arturn_days", "inv_turn", "ar_turn", "ca_turn", "fa_turn",
            "assets_turn", "op_income", "valuechange_income", "interst_income", "daa", "ebit", "ebitda", "fcff", "fcfe",
            "current_exint", "noncurrent_exint", "interestdebt", "netdebt", "tangible_asset", "working_capital",
            "networking_capital", "invest_capital", "retained_earnings", "diluted2_eps", "bps", "ocfps", "retainedps",
            "cfps", "ebit_ps", "fcff_ps", "fcfe_ps", "netprofit_margin", "grossprofit_margin", "cogs_of_sales",
            "expense_of_sales", "profit_to_gr", "saleexp_to_gr", "adminexp_of_gr", "finaexp_of_gr", "impai_ttm",
            "gc_of_gr", "op_of_gr", "ebit_of_gr", "roe", "roe_waa", "roe_dt", "roa", "npta", "roic", "roe_yearly",
            "roa2_yearly", "roe_avg", "opincome_of_ebt", "investincome_of_ebt", "n_op_profit_of_ebt", "tax_to_ebt",
            "dtprofit_to_profit", "salescash_to_or", "ocf_to_or", "ocf_to_opincome", "capitalized_to_da",
            "debt_to_assets", "assets_to_eqt", "dp_assets_to_eqt", "ca_to_assets", "nca_to_assets",
            "tbassets_to_totalassets", "int_to_talcap", "eqt_to_talcapital", "currentdebt_to_debt", "longdeb_to_debt",
            "ocf_to_shortdebt", "debt_to_eqt", "eqt_to_debt", "eqt_to_interestdebt", "tangibleasset_to_debt",
            "tangasset_to_intdebt", "tangibleasset_to_netdebt", "ocf_to_debt", "ocf_to_interestdebt", "ocf_to_netdebt",
            "ebit_to_interest", "longdebt_to_workingcapital", "ebitda_to_debt", "turn_days", "roa_yearly", "roa_dp",
            "fixed_assets", "profit_prefin_exp", "non_op_profit", "op_to_ebt", "nop_to_ebt", "ocf_to_profit",
            "cash_to_liqdebt", "cash_to_liqdebt_withinterest", "op_to_liqdebt", "op_to_debt", "roic_yearly",
            "total_fa_trun", "profit_to_op", "q_opincome", "q_investincome", "q_dtprofit", "q_eps",
            "q_netprofit_margin", "q_gsprofit_margin", "q_exp_to_sales", "q_profit_to_gr", "q_saleexp_to_gr",
            "q_adminexp_to_gr", "q_finaexp_to_gr", "q_impair_to_gr_ttm", "q_gc_to_gr", "q_op_to_gr", "q_roe",
            "q_dt_roe", "q_npta", "q_opincome_to_ebt", "q_investincome_to_ebt", "q_dtprofit_to_profit",
            "q_salescash_to_or", "q_ocf_to_sales", "q_ocf_to_or", "basic_eps_yoy", "dt_eps_yoy", "cfps_yoy", "op_yoy",
            "ebt_yoy", "netprofit_yoy", "dt_netprofit_yoy", "ocf_yoy", "roe_yoy", "bps_yoy", "assets_yoy", "eqt_yoy",
            "tr_yoy", "or_yoy", "q_gr_yoy", "q_gr_qoq", "q_sales_yoy", "q_sales_qoq", "q_op_yoy", "q_op_qoq",
            "q_profit_yoy", "q_profit_qoq", "q_netprofit_yoy", "q_netprofit_qoq", "equity_yoy", "rd_exp", "update_flag"
        ]
        column_mapping = None
        TushareDAO.__init__(self, self.engine, session_factory, TushareFinaIndicatorVip, self.database, self.table_name,
                            query_fields, entity_fields, column_mapping, config)
        DataProcess.__init__(self, "fina_indicator_vip", config)
        TuShareBase.__init__(self, "fina_indicator_vip", config, 2000)
        self.api = TushareAPI(config)

    def columns_meta(self):
        return [{
            "name": "ts_code",
            "type": "String",
            "comment": "TS代码"
        }, {
            "name": "ann_date",
            "type": "String",
            "comment": "公告日期"
        }, {
            "name": "end_date",
            "type": "String",
            "comment": "报告期"
        }, {
            "name": "eps",
            "type": "Float",
            "comment": "基本每股收益"
        }, {
            "name": "dt_eps",
            "type": "Float",
            "comment": "稀释每股收益"
        }, {
            "name": "total_revenue_ps",
            "type": "Float",
            "comment": "每股营业总收入"
        }, {
            "name": "revenue_ps",
            "type": "Float",
            "comment": "每股营业收入"
        }, {
            "name": "capital_rese_ps",
            "type": "Float",
            "comment": "每股资本公积"
        }, {
            "name": "surplus_rese_ps",
            "type": "Float",
            "comment": "每股盈余公积"
        }, {
            "name": "undist_profit_ps",
            "type": "Float",
            "comment": "每股未分配利润"
        }, {
            "name": "extra_item",
            "type": "Float",
            "comment": "非经常性损益"
        }, {
            "name": "profit_dedt",
            "type": "Float",
            "comment": "扣除非经常性损益后的净利润"
        }, {
            "name": "gross_margin",
            "type": "Float",
            "comment": "毛利"
        }, {
            "name": "current_ratio",
            "type": "Float",
            "comment": "流动比率"
        }, {
            "name": "quick_ratio",
            "type": "Float",
            "comment": "速动比率"
        }, {
            "name": "cash_ratio",
            "type": "Float",
            "comment": "保守速动比率"
        }, {
            "name": "invturn_days",
            "type": "Float",
            "comment": "存货周转天数"
        }, {
            "name": "arturn_days",
            "type": "Float",
            "comment": "应收账款周转天数"
        }, {
            "name": "inv_turn",
            "type": "Float",
            "comment": "存货周转率"
        }, {
            "name": "ar_turn",
            "type": "Float",
            "comment": "应收账款周转率"
        }, {
            "name": "ca_turn",
            "type": "Float",
            "comment": "流动资产周转率"
        }, {
            "name": "fa_turn",
            "type": "Float",
            "comment": "固定资产周转率"
        }, {
            "name": "assets_turn",
            "type": "Float",
            "comment": "总资产周转率"
        }, {
            "name": "op_income",
            "type": "Float",
            "comment": "经营活动净收益"
        }, {
            "name": "valuechange_income",
            "type": "Float",
            "comment": "价值变动净收益"
        }, {
            "name": "interst_income",
            "type": "Float",
            "comment": "利息费用"
        }, {
            "name": "daa",
            "type": "Float",
            "comment": "折旧与摊销"
        }, {
            "name": "ebit",
            "type": "Float",
            "comment": "息税前利润"
        }, {
            "name": "ebitda",
            "type": "Float",
            "comment": "息税折旧摊销前利润"
        }, {
            "name": "fcff",
            "type": "Float",
            "comment": "企业自由现金流量"
        }, {
            "name": "fcfe",
            "type": "Float",
            "comment": "股权自由现金流量"
        }, {
            "name": "current_exint",
            "type": "Float",
            "comment": "无息流动负债"
        }, {
            "name": "noncurrent_exint",
            "type": "Float",
            "comment": "无息非流动负债"
        }, {
            "name": "interestdebt",
            "type": "Float",
            "comment": "带息债务"
        }, {
            "name": "netdebt",
            "type": "Float",
            "comment": "净债务"
        }, {
            "name": "tangible_asset",
            "type": "Float",
            "comment": "有形资产"
        }, {
            "name": "working_capital",
            "type": "Float",
            "comment": "营运资金"
        }, {
            "name": "networking_capital",
            "type": "Float",
            "comment": "营运流动资本"
        }, {
            "name": "invest_capital",
            "type": "Float",
            "comment": "全部投入资本"
        }, {
            "name": "retained_earnings",
            "type": "Float",
            "comment": "留存收益"
        }, {
            "name": "diluted2_eps",
            "type": "Float",
            "comment": "期末摊薄每股收益"
        }, {
            "name": "bps",
            "type": "Float",
            "comment": "每股净资产"
        }, {
            "name": "ocfps",
            "type": "Float",
            "comment": "每股经营活动产生的现金流量净额"
        }, {
            "name": "retainedps",
            "type": "Float",
            "comment": "每股留存收益"
        }, {
            "name": "cfps",
            "type": "Float",
            "comment": "每股现金流量净额"
        }, {
            "name": "ebit_ps",
            "type": "Float",
            "comment": "每股息税前利润"
        }, {
            "name": "fcff_ps",
            "type": "Float",
            "comment": "每股企业自由现金流量"
        }, {
            "name": "fcfe_ps",
            "type": "Float",
            "comment": "每股股东自由现金流量"
        }, {
            "name": "netprofit_margin",
            "type": "Float",
            "comment": "销售净利率"
        }, {
            "name": "grossprofit_margin",
            "type": "Float",
            "comment": "销售毛利率"
        }, {
            "name": "cogs_of_sales",
            "type": "Float",
            "comment": "销售成本率"
        }, {
            "name": "expense_of_sales",
            "type": "Float",
            "comment": "销售期间费用率"
        }, {
            "name": "profit_to_gr",
            "type": "Float",
            "comment": "净利润/营业总收入"
        }, {
            "name": "saleexp_to_gr",
            "type": "Float",
            "comment": "销售费用/营业总收入"
        }, {
            "name": "adminexp_of_gr",
            "type": "Float",
            "comment": "管理费用/营业总收入"
        }, {
            "name": "finaexp_of_gr",
            "type": "Float",
            "comment": "财务费用/营业总收入"
        }, {
            "name": "impai_ttm",
            "type": "Float",
            "comment": "资产减值损失/营业总收入"
        }, {
            "name": "gc_of_gr",
            "type": "Float",
            "comment": "营业总成本/营业总收入"
        }, {
            "name": "op_of_gr",
            "type": "Float",
            "comment": "营业利润/营业总收入"
        }, {
            "name": "ebit_of_gr",
            "type": "Float",
            "comment": "息税前利润/营业总收入"
        }, {
            "name": "roe",
            "type": "Float",
            "comment": "净资产收益率"
        }, {
            "name": "roe_waa",
            "type": "Float",
            "comment": "加权平均净资产收益率"
        }, {
            "name": "roe_dt",
            "type": "Float",
            "comment": "净资产收益率(扣除非经常损益)"
        }, {
            "name": "roa",
            "type": "Float",
            "comment": "总资产报酬率"
        }, {
            "name": "npta",
            "type": "Float",
            "comment": "总资产净利润"
        }, {
            "name": "roic",
            "type": "Float",
            "comment": "投入资本回报率"
        }, {
            "name": "roe_yearly",
            "type": "Float",
            "comment": "年化净资产收益率"
        }, {
            "name": "roa2_yearly",
            "type": "Float",
            "comment": "年化总资产报酬率"
        }, {
            "name": "roe_avg",
            "type": "Float",
            "comment": "平均净资产收益率(增发条件)"
        }, {
            "name": "opincome_of_ebt",
            "type": "Float",
            "comment": "经营活动净收益/利润总额"
        }, {
            "name": "investincome_of_ebt",
            "type": "Float",
            "comment": "价值变动净收益/利润总额"
        }, {
            "name": "n_op_profit_of_ebt",
            "type": "Float",
            "comment": "营业外收支净额/利润总额"
        }, {
            "name": "tax_to_ebt",
            "type": "Float",
            "comment": "所得税/利润总额"
        }, {
            "name": "dtprofit_to_profit",
            "type": "Float",
            "comment": "扣除非经常损益后的净利润/净利润"
        }, {
            "name": "salescash_to_or",
            "type": "Float",
            "comment": "销售商品提供劳务收到的现金/营业收入"
        }, {
            "name": "ocf_to_or",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额/营业收入"
        }, {
            "name": "ocf_to_opincome",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额/经营活动净收益"
        }, {
            "name": "capitalized_to_da",
            "type": "Float",
            "comment": "资本支出/折旧和摊销"
        }, {
            "name": "debt_to_assets",
            "type": "Float",
            "comment": "资产负债率"
        }, {
            "name": "assets_to_eqt",
            "type": "Float",
            "comment": "权益乘数"
        }, {
            "name": "dp_assets_to_eqt",
            "type": "Float",
            "comment": "权益乘数(杜邦分析)"
        }, {
            "name": "ca_to_assets",
            "type": "Float",
            "comment": "流动资产/总资产"
        }, {
            "name": "nca_to_assets",
            "type": "Float",
            "comment": "非流动资产/总资产"
        }, {
            "name": "tbassets_to_totalassets",
            "type": "Float",
            "comment": "有形资产/总资产"
        }, {
            "name": "int_to_talcap",
            "type": "Float",
            "comment": "带息债务/全部投入资本"
        }, {
            "name": "eqt_to_talcapital",
            "type": "Float",
            "comment": "归属于母公司的股东权益/全部投入资本"
        }, {
            "name": "currentdebt_to_debt",
            "type": "Float",
            "comment": "流动负债/负债合计"
        }, {
            "name": "longdeb_to_debt",
            "type": "Float",
            "comment": "非流动负债/负债合计"
        }, {
            "name": "ocf_to_shortdebt",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额/流动负债"
        }, {
            "name": "debt_to_eqt",
            "type": "Float",
            "comment": "产权比率"
        }, {
            "name": "eqt_to_debt",
            "type": "Float",
            "comment": "归属于母公司的股东权益/负债合计"
        }, {
            "name": "eqt_to_interestdebt",
            "type": "Float",
            "comment": "归属于母公司的股东权益/带息债务"
        }, {
            "name": "tangibleasset_to_debt",
            "type": "Float",
            "comment": "有形资产/负债合计"
        }, {
            "name": "tangasset_to_intdebt",
            "type": "Float",
            "comment": "有形资产/带息债务"
        }, {
            "name": "tangibleasset_to_netdebt",
            "type": "Float",
            "comment": "有形资产/净债务"
        }, {
            "name": "ocf_to_debt",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额/负债合计"
        }, {
            "name": "ocf_to_interestdebt",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额/带息债务"
        }, {
            "name": "ocf_to_netdebt",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额/净债务"
        }, {
            "name": "ebit_to_interest",
            "type": "Float",
            "comment": "已获利息倍数(EBIT/利息费用)"
        }, {
            "name": "longdebt_to_workingcapital",
            "type": "Float",
            "comment": "长期债务与营运资金比率"
        }, {
            "name": "ebitda_to_debt",
            "type": "Float",
            "comment": "息税折旧摊销前利润/负债合计"
        }, {
            "name": "turn_days",
            "type": "Float",
            "comment": "营业周期"
        }, {
            "name": "roa_yearly",
            "type": "Float",
            "comment": "年化总资产净利率"
        }, {
            "name": "roa_dp",
            "type": "Float",
            "comment": "总资产净利率(杜邦分析)"
        }, {
            "name": "fixed_assets",
            "type": "Float",
            "comment": "固定资产合计"
        }, {
            "name": "profit_prefin_exp",
            "type": "Float",
            "comment": "扣除财务费用前营业利润"
        }, {
            "name": "non_op_profit",
            "type": "Float",
            "comment": "非营业利润"
        }, {
            "name": "op_to_ebt",
            "type": "Float",
            "comment": "营业利润／利润总额"
        }, {
            "name": "nop_to_ebt",
            "type": "Float",
            "comment": "非营业利润／利润总额"
        }, {
            "name": "ocf_to_profit",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额／营业利润"
        }, {
            "name": "cash_to_liqdebt",
            "type": "Float",
            "comment": "货币资金／流动负债"
        }, {
            "name": "cash_to_liqdebt_withinterest",
            "type": "Float",
            "comment": "货币资金／带息流动负债"
        }, {
            "name": "op_to_liqdebt",
            "type": "Float",
            "comment": "营业利润／流动负债"
        }, {
            "name": "op_to_debt",
            "type": "Float",
            "comment": "营业利润／负债合计"
        }, {
            "name": "roic_yearly",
            "type": "Float",
            "comment": "年化投入资本回报率"
        }, {
            "name": "total_fa_trun",
            "type": "Float",
            "comment": "固定资产合计周转率"
        }, {
            "name": "profit_to_op",
            "type": "Float",
            "comment": "利润总额／营业收入"
        }, {
            "name": "q_opincome",
            "type": "Float",
            "comment": "经营活动单季度净收益"
        }, {
            "name": "q_investincome",
            "type": "Float",
            "comment": "价值变动单季度净收益"
        }, {
            "name": "q_dtprofit",
            "type": "Float",
            "comment": "扣除非经常损益后的单季度净利润"
        }, {
            "name": "q_eps",
            "type": "Float",
            "comment": "每股收益(单季度)"
        }, {
            "name": "q_netprofit_margin",
            "type": "Float",
            "comment": "销售净利率(单季度)"
        }, {
            "name": "q_gsprofit_margin",
            "type": "Float",
            "comment": "销售毛利率(单季度)"
        }, {
            "name": "q_exp_to_sales",
            "type": "Float",
            "comment": "销售期间费用率(单季度)"
        }, {
            "name": "q_profit_to_gr",
            "type": "Float",
            "comment": "净利润／营业总收入(单季度)"
        }, {
            "name": "q_saleexp_to_gr",
            "type": "Float",
            "comment": "销售费用／营业总收入 (单季度)"
        }, {
            "name": "q_adminexp_to_gr",
            "type": "Float",
            "comment": "管理费用／营业总收入 (单季度)"
        }, {
            "name": "q_finaexp_to_gr",
            "type": "Float",
            "comment": "财务费用／营业总收入 (单季度)"
        }, {
            "name": "q_impair_to_gr_ttm",
            "type": "Float",
            "comment": "资产减值损失／营业总收入(单季度)"
        }, {
            "name": "q_gc_to_gr",
            "type": "Float",
            "comment": "营业总成本／营业总收入 (单季度)"
        }, {
            "name": "q_op_to_gr",
            "type": "Float",
            "comment": "营业利润／营业总收入(单季度)"
        }, {
            "name": "q_roe",
            "type": "Float",
            "comment": "净资产收益率(单季度)"
        }, {
            "name": "q_dt_roe",
            "type": "Float",
            "comment": "净资产单季度收益率(扣除非经常损益)"
        }, {
            "name": "q_npta",
            "type": "Float",
            "comment": "总资产净利润(单季度)"
        }, {
            "name": "q_opincome_to_ebt",
            "type": "Float",
            "comment": "经营活动净收益／利润总额(单季度)"
        }, {
            "name": "q_investincome_to_ebt",
            "type": "Float",
            "comment": "价值变动净收益／利润总额(单季度)"
        }, {
            "name": "q_dtprofit_to_profit",
            "type": "Float",
            "comment": "扣除非经常损益后的净利润／净利润(单季度)"
        }, {
            "name": "q_salescash_to_or",
            "type": "Float",
            "comment": "销售商品提供劳务收到的现金／营业收入(单季度)"
        }, {
            "name": "q_ocf_to_sales",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额／营业收入(单季度)"
        }, {
            "name": "q_ocf_to_or",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额／经营活动净收益(单季度)"
        }, {
            "name": "basic_eps_yoy",
            "type": "Float",
            "comment": "基本每股收益同比增长率(%)"
        }, {
            "name": "dt_eps_yoy",
            "type": "Float",
            "comment": "稀释每股收益同比增长率(%)"
        }, {
            "name": "cfps_yoy",
            "type": "Float",
            "comment": "每股经营活动产生的现金流量净额同比增长率(%)"
        }, {
            "name": "op_yoy",
            "type": "Float",
            "comment": "营业利润同比增长率(%)"
        }, {
            "name": "ebt_yoy",
            "type": "Float",
            "comment": "利润总额同比增长率(%)"
        }, {
            "name": "netprofit_yoy",
            "type": "Float",
            "comment": "归属母公司股东的净利润同比增长率(%)"
        }, {
            "name": "dt_netprofit_yoy",
            "type": "Float",
            "comment": "归属母公司股东的净利润-扣除非经常损益同比增长率(%)"
        }, {
            "name": "ocf_yoy",
            "type": "Float",
            "comment": "经营活动产生的现金流量净额同比增长率(%)"
        }, {
            "name": "roe_yoy",
            "type": "Float",
            "comment": "净资产收益率(摊薄)同比增长率(%)"
        }, {
            "name": "bps_yoy",
            "type": "Float",
            "comment": "每股净资产相对年初增长率(%)"
        }, {
            "name": "assets_yoy",
            "type": "Float",
            "comment": "资产总计相对年初增长率(%)"
        }, {
            "name": "eqt_yoy",
            "type": "Float",
            "comment": "归属母公司的股东权益相对年初增长率(%)"
        }, {
            "name": "tr_yoy",
            "type": "Float",
            "comment": "营业总收入同比增长率(%)"
        }, {
            "name": "or_yoy",
            "type": "Float",
            "comment": "营业收入同比增长率(%)"
        }, {
            "name": "q_gr_yoy",
            "type": "Float",
            "comment": "营业总收入同比增长率(%)(单季度)"
        }, {
            "name": "q_gr_qoq",
            "type": "Float",
            "comment": "营业总收入环比增长率(%)(单季度)"
        }, {
            "name": "q_sales_yoy",
            "type": "Float",
            "comment": "营业收入同比增长率(%)(单季度)"
        }, {
            "name": "q_sales_qoq",
            "type": "Float",
            "comment": "营业收入环比增长率(%)(单季度)"
        }, {
            "name": "q_op_yoy",
            "type": "Float",
            "comment": "营业利润同比增长率(%)(单季度)"
        }, {
            "name": "q_op_qoq",
            "type": "Float",
            "comment": "营业利润环比增长率(%)(单季度)"
        }, {
            "name": "q_profit_yoy",
            "type": "Float",
            "comment": "净利润同比增长率(%)(单季度)"
        }, {
            "name": "q_profit_qoq",
            "type": "Float",
            "comment": "净利润环比增长率(%)(单季度)"
        }, {
            "name": "q_netprofit_yoy",
            "type": "Float",
            "comment": "归属母公司股东的净利润同比增长率(%)(单季度)"
        }, {
            "name": "q_netprofit_qoq",
            "type": "Float",
            "comment": "归属母公司股东的净利润环比增长率(%)(单季度)"
        }, {
            "name": "equity_yoy",
            "type": "Float",
            "comment": "净资产同比增长率"
        }, {
            "name": "rd_exp",
            "type": "Float",
            "comment": "研发费用"
        }, {
            "name": "update_flag",
            "type": "String",
            "comment": "更新标识"
        }]

    def fina_indicator_vip(
            self,
            fields='ts_code,ann_date,end_date,eps,dt_eps,total_revenue_ps,revenue_ps,capital_rese_ps,surplus_rese_ps,undist_profit_ps,extra_item,profit_dedt,gross_margin,current_ratio,quick_ratio,cash_ratio,ar_turn,ca_turn,fa_turn,assets_turn,op_income,ebit,ebitda,fcff,fcfe,current_exint,noncurrent_exint,interestdebt,netdebt,tangible_asset,working_capital,networking_capital,invest_capital,retained_earnings,diluted2_eps,bps,ocfps,retainedps,cfps,ebit_ps,fcff_ps,fcfe_ps,netprofit_margin,grossprofit_margin,cogs_of_sales,expense_of_sales,profit_to_gr,saleexp_to_gr,adminexp_of_gr,finaexp_of_gr,impai_ttm,gc_of_gr,op_of_gr,ebit_of_gr,roe,roe_waa,roe_dt,roa,npta,roic,roe_yearly,roa2_yearly,debt_to_assets,assets_to_eqt,dp_assets_to_eqt,ca_to_assets,nca_to_assets,tbassets_to_totalassets,int_to_talcap,eqt_to_talcapital,currentdebt_to_debt,longdeb_to_debt,ocf_to_shortdebt,debt_to_eqt,eqt_to_debt,eqt_to_interestdebt,tangibleasset_to_debt,tangasset_to_intdebt,tangibleasset_to_netdebt,ocf_to_debt,turn_days,roa_yearly,roa_dp,fixed_assets,profit_to_op,q_saleexp_to_gr,q_gc_to_gr,q_roe,q_dt_roe,q_npta,q_ocf_to_sales,basic_eps_yoy,dt_eps_yoy,cfps_yoy,op_yoy,ebt_yoy,netprofit_yoy,dt_netprofit_yoy,ocf_yoy,roe_yoy,bps_yoy,assets_yoy,eqt_yoy,tr_yoy,or_yoy,q_sales_yoy,q_op_qoq,equity_yoy',
            **kwargs):
        """
        获取上市公司财务指标数据
        | Arguments:
        | ts_code(str): required  股票代码
        | ann_date(str):   公告日期
        | start_date(str):   报告期开始日期
        | end_date(str):   报告期结束日期
        | period(str):   报告期
        | update_flag(str):   更新标志
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码 Y
         ann_date(str)  公告日期 Y
         end_date(str)  报告期 Y
         eps(float)  基本每股收益 Y
         dt_eps(float)  稀释每股收益 Y
         total_revenue_ps(float)  每股营业总收入 Y
         revenue_ps(float)  每股营业收入 Y
         capital_rese_ps(float)  每股资本公积 Y
         surplus_rese_ps(float)  每股盈余公积 Y
         undist_profit_ps(float)  每股未分配利润 Y
         extra_item(float)  非经常性损益 Y
         profit_dedt(float)  扣除非经常性损益后的净利润 Y
         gross_margin(float)  毛利 Y
         current_ratio(float)  流动比率 Y
         quick_ratio(float)  速动比率 Y
         cash_ratio(float)  保守速动比率 Y
         invturn_days(float)  存货周转天数 N
         arturn_days(float)  应收账款周转天数 N
         inv_turn(float)  存货周转率 N
         ar_turn(float)  应收账款周转率 Y
         ca_turn(float)  流动资产周转率 Y
         fa_turn(float)  固定资产周转率 Y
         assets_turn(float)  总资产周转率 Y
         op_income(float)  经营活动净收益 Y
         valuechange_income(float)  价值变动净收益 N
         interst_income(float)  利息费用 N
         daa(float)  折旧与摊销 N
         ebit(float)  息税前利润 Y
         ebitda(float)  息税折旧摊销前利润 Y
         fcff(float)  企业自由现金流量 Y
         fcfe(float)  股权自由现金流量 Y
         current_exint(float)  无息流动负债 Y
         noncurrent_exint(float)  无息非流动负债 Y
         interestdebt(float)  带息债务 Y
         netdebt(float)  净债务 Y
         tangible_asset(float)  有形资产 Y
         working_capital(float)  营运资金 Y
         networking_capital(float)  营运流动资本 Y
         invest_capital(float)  全部投入资本 Y
         retained_earnings(float)  留存收益 Y
         diluted2_eps(float)  期末摊薄每股收益 Y
         bps(float)  每股净资产 Y
         ocfps(float)  每股经营活动产生的现金流量净额 Y
         retainedps(float)  每股留存收益 Y
         cfps(float)  每股现金流量净额 Y
         ebit_ps(float)  每股息税前利润 Y
         fcff_ps(float)  每股企业自由现金流量 Y
         fcfe_ps(float)  每股股东自由现金流量 Y
         netprofit_margin(float)  销售净利率 Y
         grossprofit_margin(float)  销售毛利率 Y
         cogs_of_sales(float)  销售成本率 Y
         expense_of_sales(float)  销售期间费用率 Y
         profit_to_gr(float)  净利润/营业总收入 Y
         saleexp_to_gr(float)  销售费用/营业总收入 Y
         adminexp_of_gr(float)  管理费用/营业总收入 Y
         finaexp_of_gr(float)  财务费用/营业总收入 Y
         impai_ttm(float)  资产减值损失/营业总收入 Y
         gc_of_gr(float)  营业总成本/营业总收入 Y
         op_of_gr(float)  营业利润/营业总收入 Y
         ebit_of_gr(float)  息税前利润/营业总收入 Y
         roe(float)  净资产收益率 Y
         roe_waa(float)  加权平均净资产收益率 Y
         roe_dt(float)  净资产收益率(扣除非经常损益) Y
         roa(float)  总资产报酬率 Y
         npta(float)  总资产净利润 Y
         roic(float)  投入资本回报率 Y
         roe_yearly(float)  年化净资产收益率 Y
         roa2_yearly(float)  年化总资产报酬率 Y
         roe_avg(float)  平均净资产收益率(增发条件) N
         opincome_of_ebt(float)  经营活动净收益/利润总额 N
         investincome_of_ebt(float)  价值变动净收益/利润总额 N
         n_op_profit_of_ebt(float)  营业外收支净额/利润总额 N
         tax_to_ebt(float)  所得税/利润总额 N
         dtprofit_to_profit(float)  扣除非经常损益后的净利润/净利润 N
         salescash_to_or(float)  销售商品提供劳务收到的现金/营业收入 N
         ocf_to_or(float)  经营活动产生的现金流量净额/营业收入 N
         ocf_to_opincome(float)  经营活动产生的现金流量净额/经营活动净收益 N
         capitalized_to_da(float)  资本支出/折旧和摊销 N
         debt_to_assets(float)  资产负债率 Y
         assets_to_eqt(float)  权益乘数 Y
         dp_assets_to_eqt(float)  权益乘数(杜邦分析) Y
         ca_to_assets(float)  流动资产/总资产 Y
         nca_to_assets(float)  非流动资产/总资产 Y
         tbassets_to_totalassets(float)  有形资产/总资产 Y
         int_to_talcap(float)  带息债务/全部投入资本 Y
         eqt_to_talcapital(float)  归属于母公司的股东权益/全部投入资本 Y
         currentdebt_to_debt(float)  流动负债/负债合计 Y
         longdeb_to_debt(float)  非流动负债/负债合计 Y
         ocf_to_shortdebt(float)  经营活动产生的现金流量净额/流动负债 Y
         debt_to_eqt(float)  产权比率 Y
         eqt_to_debt(float)  归属于母公司的股东权益/负债合计 Y
         eqt_to_interestdebt(float)  归属于母公司的股东权益/带息债务 Y
         tangibleasset_to_debt(float)  有形资产/负债合计 Y
         tangasset_to_intdebt(float)  有形资产/带息债务 Y
         tangibleasset_to_netdebt(float)  有形资产/净债务 Y
         ocf_to_debt(float)  经营活动产生的现金流量净额/负债合计 Y
         ocf_to_interestdebt(float)  经营活动产生的现金流量净额/带息债务 N
         ocf_to_netdebt(float)  经营活动产生的现金流量净额/净债务 N
         ebit_to_interest(float)  已获利息倍数(EBIT/利息费用) N
         longdebt_to_workingcapital(float)  长期债务与营运资金比率 N
         ebitda_to_debt(float)  息税折旧摊销前利润/负债合计 N
         turn_days(float)  营业周期 Y
         roa_yearly(float)  年化总资产净利率 Y
         roa_dp(float)  总资产净利率(杜邦分析) Y
         fixed_assets(float)  固定资产合计 Y
         profit_prefin_exp(float)  扣除财务费用前营业利润 N
         non_op_profit(float)  非营业利润 N
         op_to_ebt(float)  营业利润／利润总额 N
         nop_to_ebt(float)  非营业利润／利润总额 N
         ocf_to_profit(float)  经营活动产生的现金流量净额／营业利润 N
         cash_to_liqdebt(float)  货币资金／流动负债 N
         cash_to_liqdebt_withinterest(float)  货币资金／带息流动负债 N
         op_to_liqdebt(float)  营业利润／流动负债 N
         op_to_debt(float)  营业利润／负债合计 N
         roic_yearly(float)  年化投入资本回报率 N
         total_fa_trun(float)  固定资产合计周转率 N
         profit_to_op(float)  利润总额／营业收入 Y
         q_opincome(float)  经营活动单季度净收益 N
         q_investincome(float)  价值变动单季度净收益 N
         q_dtprofit(float)  扣除非经常损益后的单季度净利润 N
         q_eps(float)  每股收益(单季度) N
         q_netprofit_margin(float)  销售净利率(单季度) N
         q_gsprofit_margin(float)  销售毛利率(单季度) N
         q_exp_to_sales(float)  销售期间费用率(单季度) N
         q_profit_to_gr(float)  净利润／营业总收入(单季度) N
         q_saleexp_to_gr(float)  销售费用／营业总收入 (单季度) Y
         q_adminexp_to_gr(float)  管理费用／营业总收入 (单季度) N
         q_finaexp_to_gr(float)  财务费用／营业总收入 (单季度) N
         q_impair_to_gr_ttm(float)  资产减值损失／营业总收入(单季度) N
         q_gc_to_gr(float)  营业总成本／营业总收入 (单季度) Y
         q_op_to_gr(float)  营业利润／营业总收入(单季度) N
         q_roe(float)  净资产收益率(单季度) Y
         q_dt_roe(float)  净资产单季度收益率(扣除非经常损益) Y
         q_npta(float)  总资产净利润(单季度) Y
         q_opincome_to_ebt(float)  经营活动净收益／利润总额(单季度) N
         q_investincome_to_ebt(float)  价值变动净收益／利润总额(单季度) N
         q_dtprofit_to_profit(float)  扣除非经常损益后的净利润／净利润(单季度) N
         q_salescash_to_or(float)  销售商品提供劳务收到的现金／营业收入(单季度) N
         q_ocf_to_sales(float)  经营活动产生的现金流量净额／营业收入(单季度) Y
         q_ocf_to_or(float)  经营活动产生的现金流量净额／经营活动净收益(单季度) N
         basic_eps_yoy(float)  基本每股收益同比增长率(%) Y
         dt_eps_yoy(float)  稀释每股收益同比增长率(%) Y
         cfps_yoy(float)  每股经营活动产生的现金流量净额同比增长率(%) Y
         op_yoy(float)  营业利润同比增长率(%) Y
         ebt_yoy(float)  利润总额同比增长率(%) Y
         netprofit_yoy(float)  归属母公司股东的净利润同比增长率(%) Y
         dt_netprofit_yoy(float)  归属母公司股东的净利润-扣除非经常损益同比增长率(%) Y
         ocf_yoy(float)  经营活动产生的现金流量净额同比增长率(%) Y
         roe_yoy(float)  净资产收益率(摊薄)同比增长率(%) Y
         bps_yoy(float)  每股净资产相对年初增长率(%) Y
         assets_yoy(float)  资产总计相对年初增长率(%) Y
         eqt_yoy(float)  归属母公司的股东权益相对年初增长率(%) Y
         tr_yoy(float)  营业总收入同比增长率(%) Y
         or_yoy(float)  营业收入同比增长率(%) Y
         q_gr_yoy(float)  营业总收入同比增长率(%)(单季度) N
         q_gr_qoq(float)  营业总收入环比增长率(%)(单季度) N
         q_sales_yoy(float)  营业收入同比增长率(%)(单季度) Y
         q_sales_qoq(float)  营业收入环比增长率(%)(单季度) N
         q_op_yoy(float)  营业利润同比增长率(%)(单季度) N
         q_op_qoq(float)  营业利润环比增长率(%)(单季度) Y
         q_profit_yoy(float)  净利润同比增长率(%)(单季度) N
         q_profit_qoq(float)  净利润环比增长率(%)(单季度) N
         q_netprofit_yoy(float)  归属母公司股东的净利润同比增长率(%)(单季度) N
         q_netprofit_qoq(float)  归属母公司股东的净利润环比增长率(%)(单季度) N
         equity_yoy(float)  净资产同比增长率 Y
         rd_exp(float)  研发费用 N
         update_flag(str)  更新标识 N
        
        """
        return super().query(fields, **kwargs)

    def process(self, **kwargs):
        """
        同步历史数据
        :return:
        """
        return super()._process(self.fetch_and_append,
                                BatchWriter(self.engine, self.table_name, self.schema, self.database_dir), **kwargs)

    def fetch_and_append(self, **kwargs):
        """
        获取tushare数据并append到数据库中
        :return: 数量行数
        """
        init_args = {
            "ts_code": "",
            "ann_date": "",
            "start_date": "",
            "end_date": "",
            "period": "",
            "update_flag": "",
            "limit": "",
            "offset": ""
        }
        is_test = kwargs.get('test') or False
        if len(kwargs.keys()) == 0:
            kwargs = init_args
        # 初始化offset和limit
        if not kwargs.get("limit"):
            kwargs['limit'] = self.default_limit()
        init_offset = 0
        offset = 0
        if kwargs.get('offset'):
            offset = int(kwargs['offset'])
            init_offset = offset

        kwargs = {key: kwargs[key] for key in kwargs.keys() & init_args.keys()}

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.fina_indicator_vip with args: {}".format(kwargs))
                return self.tushare_query('fina_indicator_vip', fields=self.tushare_fields, **kwargs)
            except Exception as err:
                raise ProcessException(kwargs, err)

        res = fetch_save(offset)
        size = res.size()
        offset += size
        res.fields = self.entity_fields
        if is_test:
            return res
        while kwargs['limit'] != "" and size == int(kwargs['limit']):
            result = fetch_save(offset)
            size = result.size()
            offset += size
            res.append(result)
        return res


extends_attr(FinaIndicatorVip, fina_indicator_vip_ext)

if __name__ == '__main__':
    import tushare as ts
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.fina_indicator_vip())

    api = FinaIndicatorVip(config)
    print(api.process())    # 同步增量数据
    print(api.fina_indicator_vip())    # 数据查询接口
