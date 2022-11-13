"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare fina_indicator_vip接口
数据接口-沪深股票-财务数据-财务指标数据  https://tushare.pro/document/2?doc_id=7900

@author: rmfish
"""
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.api.tushare.base_dao import BaseDao
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.extends.fina_indicator_vip_ext import *
from tutake.api.tushare.process import ProcessType, DataProcess
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import tutake_config
from tutake.utils.decorator import sleep

engine = create_engine("%s/%s" % (tutake_config.get_data_sqlite_driver_url(), 'tushare_fina_indicator_vip.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)
Base = declarative_base()


class TushareFinaIndicatorVip(Base):
    __tablename__ = "tushare_fina_indicator_vip"
    id = Column(Integer, primary_key=True, autoincrement=True)
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


TushareFinaIndicatorVip.__table__.create(bind=engine, checkfirst=True)


class FinaIndicatorVip(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        query_fields = ['ts_code', 'ann_date', 'start_date', 'end_date', 'period', 'update_flag', 'limit', 'offset']
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
        BaseDao.__init__(self, engine, session_factory, TushareFinaIndicatorVip, 'tushare_fina_indicator_vip',
                         query_fields, entity_fields)
        TuShareBase.__init__(self)
        DataProcess.__init__(self, "fina_indicator_vip")
        self.dao = DAO()

    def fina_indicator_vip(self, fields='', **kwargs):
        """
        
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
         ts_code(str)  TS代码
         ann_date(str)  公告日期
         end_date(str)  报告期
         eps(float)  基本每股收益
         dt_eps(float)  稀释每股收益
         total_revenue_ps(float)  每股营业总收入
         revenue_ps(float)  每股营业收入
         capital_rese_ps(float)  每股资本公积
         surplus_rese_ps(float)  每股盈余公积
         undist_profit_ps(float)  每股未分配利润
         extra_item(float)  非经常性损益
         profit_dedt(float)  扣除非经常性损益后的净利润
         gross_margin(float)  毛利
         current_ratio(float)  流动比率
         quick_ratio(float)  速动比率
         cash_ratio(float)  保守速动比率
         invturn_days(float)  存货周转天数
         arturn_days(float)  应收账款周转天数
         inv_turn(float)  存货周转率
         ar_turn(float)  应收账款周转率
         ca_turn(float)  流动资产周转率
         fa_turn(float)  固定资产周转率
         assets_turn(float)  总资产周转率
         op_income(float)  经营活动净收益
         valuechange_income(float)  价值变动净收益
         interst_income(float)  利息费用
         daa(float)  折旧与摊销
         ebit(float)  息税前利润
         ebitda(float)  息税折旧摊销前利润
         fcff(float)  企业自由现金流量
         fcfe(float)  股权自由现金流量
         current_exint(float)  无息流动负债
         noncurrent_exint(float)  无息非流动负债
         interestdebt(float)  带息债务
         netdebt(float)  净债务
         tangible_asset(float)  有形资产
         working_capital(float)  营运资金
         networking_capital(float)  营运流动资本
         invest_capital(float)  全部投入资本
         retained_earnings(float)  留存收益
         diluted2_eps(float)  期末摊薄每股收益
         bps(float)  每股净资产
         ocfps(float)  每股经营活动产生的现金流量净额
         retainedps(float)  每股留存收益
         cfps(float)  每股现金流量净额
         ebit_ps(float)  每股息税前利润
         fcff_ps(float)  每股企业自由现金流量
         fcfe_ps(float)  每股股东自由现金流量
         netprofit_margin(float)  销售净利率
         grossprofit_margin(float)  销售毛利率
         cogs_of_sales(float)  销售成本率
         expense_of_sales(float)  销售期间费用率
         profit_to_gr(float)  净利润/营业总收入
         saleexp_to_gr(float)  销售费用/营业总收入
         adminexp_of_gr(float)  管理费用/营业总收入
         finaexp_of_gr(float)  财务费用/营业总收入
         impai_ttm(float)  资产减值损失/营业总收入
         gc_of_gr(float)  营业总成本/营业总收入
         op_of_gr(float)  营业利润/营业总收入
         ebit_of_gr(float)  息税前利润/营业总收入
         roe(float)  净资产收益率
         roe_waa(float)  加权平均净资产收益率
         roe_dt(float)  净资产收益率(扣除非经常损益)
         roa(float)  总资产报酬率
         npta(float)  总资产净利润
         roic(float)  投入资本回报率
         roe_yearly(float)  年化净资产收益率
         roa2_yearly(float)  年化总资产报酬率
         roe_avg(float)  平均净资产收益率(增发条件)
         opincome_of_ebt(float)  经营活动净收益/利润总额
         investincome_of_ebt(float)  价值变动净收益/利润总额
         n_op_profit_of_ebt(float)  营业外收支净额/利润总额
         tax_to_ebt(float)  所得税/利润总额
         dtprofit_to_profit(float)  扣除非经常损益后的净利润/净利润
         salescash_to_or(float)  销售商品提供劳务收到的现金/营业收入
         ocf_to_or(float)  经营活动产生的现金流量净额/营业收入
         ocf_to_opincome(float)  经营活动产生的现金流量净额/经营活动净收益
         capitalized_to_da(float)  资本支出/折旧和摊销
         debt_to_assets(float)  资产负债率
         assets_to_eqt(float)  权益乘数
         dp_assets_to_eqt(float)  权益乘数(杜邦分析)
         ca_to_assets(float)  流动资产/总资产
         nca_to_assets(float)  非流动资产/总资产
         tbassets_to_totalassets(float)  有形资产/总资产
         int_to_talcap(float)  带息债务/全部投入资本
         eqt_to_talcapital(float)  归属于母公司的股东权益/全部投入资本
         currentdebt_to_debt(float)  流动负债/负债合计
         longdeb_to_debt(float)  非流动负债/负债合计
         ocf_to_shortdebt(float)  经营活动产生的现金流量净额/流动负债
         debt_to_eqt(float)  产权比率
         eqt_to_debt(float)  归属于母公司的股东权益/负债合计
         eqt_to_interestdebt(float)  归属于母公司的股东权益/带息债务
         tangibleasset_to_debt(float)  有形资产/负债合计
         tangasset_to_intdebt(float)  有形资产/带息债务
         tangibleasset_to_netdebt(float)  有形资产/净债务
         ocf_to_debt(float)  经营活动产生的现金流量净额/负债合计
         ocf_to_interestdebt(float)  经营活动产生的现金流量净额/带息债务
         ocf_to_netdebt(float)  经营活动产生的现金流量净额/净债务
         ebit_to_interest(float)  已获利息倍数(EBIT/利息费用)
         longdebt_to_workingcapital(float)  长期债务与营运资金比率
         ebitda_to_debt(float)  息税折旧摊销前利润/负债合计
         turn_days(float)  营业周期
         roa_yearly(float)  年化总资产净利率
         roa_dp(float)  总资产净利率(杜邦分析)
         fixed_assets(float)  固定资产合计
         profit_prefin_exp(float)  扣除财务费用前营业利润
         non_op_profit(float)  非营业利润
         op_to_ebt(float)  营业利润／利润总额
         nop_to_ebt(float)  非营业利润／利润总额
         ocf_to_profit(float)  经营活动产生的现金流量净额／营业利润
         cash_to_liqdebt(float)  货币资金／流动负债
         cash_to_liqdebt_withinterest(float)  货币资金／带息流动负债
         op_to_liqdebt(float)  营业利润／流动负债
         op_to_debt(float)  营业利润／负债合计
         roic_yearly(float)  年化投入资本回报率
         total_fa_trun(float)  固定资产合计周转率
         profit_to_op(float)  利润总额／营业收入
         q_opincome(float)  经营活动单季度净收益
         q_investincome(float)  价值变动单季度净收益
         q_dtprofit(float)  扣除非经常损益后的单季度净利润
         q_eps(float)  每股收益(单季度)
         q_netprofit_margin(float)  销售净利率(单季度)
         q_gsprofit_margin(float)  销售毛利率(单季度)
         q_exp_to_sales(float)  销售期间费用率(单季度)
         q_profit_to_gr(float)  净利润／营业总收入(单季度)
         q_saleexp_to_gr(float)  销售费用／营业总收入 (单季度)
         q_adminexp_to_gr(float)  管理费用／营业总收入 (单季度)
         q_finaexp_to_gr(float)  财务费用／营业总收入 (单季度)
         q_impair_to_gr_ttm(float)  资产减值损失／营业总收入(单季度)
         q_gc_to_gr(float)  营业总成本／营业总收入 (单季度)
         q_op_to_gr(float)  营业利润／营业总收入(单季度)
         q_roe(float)  净资产收益率(单季度)
         q_dt_roe(float)  净资产单季度收益率(扣除非经常损益)
         q_npta(float)  总资产净利润(单季度)
         q_opincome_to_ebt(float)  经营活动净收益／利润总额(单季度)
         q_investincome_to_ebt(float)  价值变动净收益／利润总额(单季度)
         q_dtprofit_to_profit(float)  扣除非经常损益后的净利润／净利润(单季度)
         q_salescash_to_or(float)  销售商品提供劳务收到的现金／营业收入(单季度)
         q_ocf_to_sales(float)  经营活动产生的现金流量净额／营业收入(单季度)
         q_ocf_to_or(float)  经营活动产生的现金流量净额／经营活动净收益(单季度)
         basic_eps_yoy(float)  基本每股收益同比增长率(%)
         dt_eps_yoy(float)  稀释每股收益同比增长率(%)
         cfps_yoy(float)  每股经营活动产生的现金流量净额同比增长率(%)
         op_yoy(float)  营业利润同比增长率(%)
         ebt_yoy(float)  利润总额同比增长率(%)
         netprofit_yoy(float)  归属母公司股东的净利润同比增长率(%)
         dt_netprofit_yoy(float)  归属母公司股东的净利润-扣除非经常损益同比增长率(%)
         ocf_yoy(float)  经营活动产生的现金流量净额同比增长率(%)
         roe_yoy(float)  净资产收益率(摊薄)同比增长率(%)
         bps_yoy(float)  每股净资产相对年初增长率(%)
         assets_yoy(float)  资产总计相对年初增长率(%)
         eqt_yoy(float)  归属母公司的股东权益相对年初增长率(%)
         tr_yoy(float)  营业总收入同比增长率(%)
         or_yoy(float)  营业收入同比增长率(%)
         q_gr_yoy(float)  营业总收入同比增长率(%)(单季度)
         q_gr_qoq(float)  营业总收入环比增长率(%)(单季度)
         q_sales_yoy(float)  营业收入同比增长率(%)(单季度)
         q_sales_qoq(float)  营业收入环比增长率(%)(单季度)
         q_op_yoy(float)  营业利润同比增长率(%)(单季度)
         q_op_qoq(float)  营业利润环比增长率(%)(单季度)
         q_profit_yoy(float)  净利润同比增长率(%)(单季度)
         q_profit_qoq(float)  净利润环比增长率(%)(单季度)
         q_netprofit_yoy(float)  归属母公司股东的净利润同比增长率(%)(单季度)
         q_netprofit_qoq(float)  归属母公司股东的净利润环比增长率(%)(单季度)
         equity_yoy(float)  净资产同比增长率
         rd_exp(float)  研发费用
         update_flag(str)  更新标识
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType):
        """
        同步历史数据
        :return:
        """
        return super()._process(process_type, self.fetch_and_append)

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

        @sleep(timeout=61, time_append=60, retry=20, match="^抱歉，您每分钟最多访问该接口")
        def fetch_save(offset_val=0):
            kwargs['offset'] = str(offset_val)
            self.logger.debug("Invoke pro.fina_indicator_vip with args: {}".format(kwargs))
            res = self.tushare_api().fina_indicator_vip(**kwargs, fields=self.entity_fields)
            res.to_sql('tushare_fina_indicator_vip',
                       con=engine,
                       if_exists='append',
                       index=False,
                       index_label=['ts_code'])
            return res

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(FinaIndicatorVip, 'default_limit', default_limit_ext)
setattr(FinaIndicatorVip, 'default_order_by', default_order_by_ext)
setattr(FinaIndicatorVip, 'prepare', prepare_ext)
setattr(FinaIndicatorVip, 'tushare_parameters', tushare_parameters_ext)
setattr(FinaIndicatorVip, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    api = FinaIndicatorVip()
    # api.process(ProcessType.HISTORY)  # 同步历史数据
    api.process(ProcessType.INCREASE)    # 同步增量数据
    print(api.fina_indicator_vip())    # 数据查询接口
