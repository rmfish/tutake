"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare income_vip接口
获取上市公司财务利润表数据
数据接口-沪深股票-财务数据-利润表  https://tushare.pro/document/2?doc_id=3300

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.tushare.income_vip_ext import *
from tutake.api.tushare.base_dao import BaseDao, Base
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareIncomeVip(Base):
    __tablename__ = "tushare_income_vip"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS代码')
    ann_date = Column(String, index=True, comment='公告日期')
    f_ann_date = Column(String, index=True, comment='实际公告日期')
    end_date = Column(String, index=True, comment='报告期')
    report_type = Column(
        String,
        index=True,
        comment=
        '报告类型 1合并报表 2单季合并 3调整单季合并表 4调整合并报表 5调整前合并报表 6母公司报表 7母公司单季表 8 母公司调整单季表 9母公司调整表 10母公司调整前报表 11调整前合并报表 12母公司调整前报表')
    comp_type = Column(String, index=True, comment='公司类型(1一般工商业2银行3保险4证券)')
    end_type = Column(String, index=True, comment='报告期类型')
    basic_eps = Column(Float, comment='基本每股收益')
    diluted_eps = Column(Float, comment='稀释每股收益')
    total_revenue = Column(Float, comment='营业总收入')
    revenue = Column(Float, comment='营业收入')
    int_income = Column(Float, comment='利息收入')
    prem_earned = Column(Float, comment='已赚保费')
    comm_income = Column(Float, comment='手续费及佣金收入')
    n_commis_income = Column(Float, comment='手续费及佣金净收入')
    n_oth_income = Column(Float, comment='其他经营净收益')
    n_oth_b_income = Column(Float, comment='加:其他业务净收益')
    prem_income = Column(Float, comment='保险业务收入')
    out_prem = Column(Float, comment='减:分出保费')
    une_prem_reser = Column(Float, comment='提取未到期责任准备金')
    reins_income = Column(Float, comment='其中:分保费收入')
    n_sec_tb_income = Column(Float, comment='代理买卖证券业务净收入')
    n_sec_uw_income = Column(Float, comment='证券承销业务净收入')
    n_asset_mg_income = Column(Float, comment='受托客户资产管理业务净收入')
    oth_b_income = Column(Float, comment='其他业务收入')
    fv_value_chg_gain = Column(Float, comment='加:公允价值变动净收益')
    invest_income = Column(Float, comment='加:投资净收益')
    ass_invest_income = Column(Float, comment='其中:对联营企业和合营企业的投资收益')
    forex_gain = Column(Float, comment='加:汇兑净收益')
    total_cogs = Column(Float, comment='营业总成本')
    oper_cost = Column(Float, comment='减:营业成本')
    int_exp = Column(Float, comment='减:利息支出')
    comm_exp = Column(Float, comment='减:手续费及佣金支出')
    biz_tax_surchg = Column(Float, comment='减:营业税金及附加')
    sell_exp = Column(Float, comment='减:销售费用')
    admin_exp = Column(Float, comment='减:管理费用')
    fin_exp = Column(Float, comment='减:财务费用')
    assets_impair_loss = Column(Float, comment='减:资产减值损失')
    prem_refund = Column(Float, comment='退保金')
    compens_payout = Column(Float, comment='赔付总支出')
    reser_insur_liab = Column(Float, comment='提取保险责任准备金')
    div_payt = Column(Float, comment='保户红利支出')
    reins_exp = Column(Float, comment='分保费用')
    oper_exp = Column(Float, comment='营业支出')
    compens_payout_refu = Column(Float, comment='减:摊回赔付支出')
    insur_reser_refu = Column(Float, comment='减:摊回保险责任准备金')
    reins_cost_refund = Column(Float, comment='减:摊回分保费用')
    other_bus_cost = Column(Float, comment='其他业务成本')
    operate_profit = Column(Float, comment='营业利润')
    non_oper_income = Column(Float, comment='加:营业外收入')
    non_oper_exp = Column(Float, comment='减:营业外支出')
    nca_disploss = Column(Float, comment='其中:减:非流动资产处置净损失')
    total_profit = Column(Float, comment='利润总额')
    income_tax = Column(Float, comment='所得税费用')
    n_income = Column(Float, comment='净利润(含少数股东损益)')
    n_income_attr_p = Column(Float, comment='净利润(不含少数股东损益)')
    minority_gain = Column(Float, comment='少数股东损益')
    oth_compr_income = Column(Float, comment='其他综合收益')
    t_compr_income = Column(Float, comment='综合收益总额')
    compr_inc_attr_p = Column(Float, comment='归属于母公司(或股东)的综合收益总额')
    compr_inc_attr_m_s = Column(Float, comment='归属于少数股东的综合收益总额')
    ebit = Column(Float, comment='息税前利润')
    ebitda = Column(Float, comment='息税折旧摊销前利润')
    insurance_exp = Column(Float, comment='保险业务支出')
    undist_profit = Column(Float, comment='年初未分配利润')
    distable_profit = Column(Float, comment='可分配利润')
    rd_exp = Column(Float, comment='研发费用')
    fin_exp_int_exp = Column(Float, comment='财务费用:利息费用')
    fin_exp_int_inc = Column(Float, comment='财务费用:利息收入')
    transfer_surplus_rese = Column(Float, comment='盈余公积转入')
    transfer_housing_imprest = Column(Float, comment='住房周转金转入')
    transfer_oth = Column(Float, comment='其他转入')
    adj_lossgain = Column(Float, comment='调整以前年度损益')
    withdra_legal_surplus = Column(Float, comment='提取法定盈余公积')
    withdra_legal_pubfund = Column(Float, comment='提取法定公益金')
    withdra_biz_devfund = Column(Float, comment='提取企业发展基金')
    withdra_rese_fund = Column(Float, comment='提取储备基金')
    withdra_oth_ersu = Column(Float, comment='提取任意盈余公积金')
    workers_welfare = Column(Float, comment='职工奖金福利')
    distr_profit_shrhder = Column(Float, comment='可供股东分配的利润')
    prfshare_payable_dvd = Column(Float, comment='应付优先股股利')
    comshare_payable_dvd = Column(Float, comment='应付普通股股利')
    capit_comstock_div = Column(Float, comment='转作股本的普通股股利')
    net_after_nr_lp_correct = Column(Float, comment='扣除非经常性损益后的净利润（更正前）')
    oth_income = Column(Float, comment='其他收益')
    asset_disp_income = Column(Float, comment='资产处置收益')
    continued_net_profit = Column(Float, comment='持续经营净利润')
    end_net_profit = Column(Float, comment='终止经营净利润')
    credit_impa_loss = Column(Float, comment='信用减值损失')
    net_expo_hedging_benefits = Column(Float, comment='净敞口套期收益')
    oth_impair_loss_assets = Column(Float, comment='其他资产减值损失')
    total_opcost = Column(Float, comment='营业总成本2')
    amodcost_fin_assets = Column(Float, comment='以摊余成本计量的金融资产终止确认收益')
    update_flag = Column(String, comment='更新标识')


class IncomeVip(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_income_vip.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareIncomeVip.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = [
            'ts_code', 'ann_date', 'f_ann_date', 'start_date', 'end_date', 'period', 'report_type', 'comp_type',
            'end_type', 'is_calc', 'limit', 'offset'
        ]
        entity_fields = [
            "ts_code", "ann_date", "f_ann_date", "end_date", "report_type", "comp_type", "end_type", "basic_eps",
            "diluted_eps", "total_revenue", "revenue", "int_income", "prem_earned", "comm_income", "n_commis_income",
            "n_oth_income", "n_oth_b_income", "prem_income", "out_prem", "une_prem_reser", "reins_income",
            "n_sec_tb_income", "n_sec_uw_income", "n_asset_mg_income", "oth_b_income", "fv_value_chg_gain",
            "invest_income", "ass_invest_income", "forex_gain", "total_cogs", "oper_cost", "int_exp", "comm_exp",
            "biz_tax_surchg", "sell_exp", "admin_exp", "fin_exp", "assets_impair_loss", "prem_refund", "compens_payout",
            "reser_insur_liab", "div_payt", "reins_exp", "oper_exp", "compens_payout_refu", "insur_reser_refu",
            "reins_cost_refund", "other_bus_cost", "operate_profit", "non_oper_income", "non_oper_exp", "nca_disploss",
            "total_profit", "income_tax", "n_income", "n_income_attr_p", "minority_gain", "oth_compr_income",
            "t_compr_income", "compr_inc_attr_p", "compr_inc_attr_m_s", "ebit", "ebitda", "insurance_exp",
            "undist_profit", "distable_profit", "rd_exp", "fin_exp_int_exp", "fin_exp_int_inc", "transfer_surplus_rese",
            "transfer_housing_imprest", "transfer_oth", "adj_lossgain", "withdra_legal_surplus",
            "withdra_legal_pubfund", "withdra_biz_devfund", "withdra_rese_fund", "withdra_oth_ersu", "workers_welfare",
            "distr_profit_shrhder", "prfshare_payable_dvd", "comshare_payable_dvd", "capit_comstock_div",
            "net_after_nr_lp_correct", "oth_income", "asset_disp_income", "continued_net_profit", "end_net_profit",
            "credit_impa_loss", "net_expo_hedging_benefits", "oth_impair_loss_assets", "total_opcost",
            "amodcost_fin_assets", "update_flag"
        ]
        BaseDao.__init__(self, self.engine, session_factory, TushareIncomeVip, 'tushare_income_vip', query_fields,
                         entity_fields)
        DataProcess.__init__(self, "income_vip", config)
        TuShareBase.__init__(self, "income_vip", config, 5000)
        self.dao = DAO()

    def income_vip(self, fields='', **kwargs):
        """
        获取上市公司财务利润表数据
        | Arguments:
        | ts_code(str): required  股票代码
        | ann_date(str):   公告日期
        | f_ann_date(str):   实际公告日期
        | start_date(str):   报告期开始日期
        | end_date(str):   报告期结束日期
        | period(str):   报告期
        | report_type(str):   报告类型
        | comp_type(str):   公司类型
        | end_type(str):   报告期编码，1~4表示季度
        | is_calc(int):   是否计算报表
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS代码
         ann_date(str)  公告日期
         f_ann_date(str)  实际公告日期
         end_date(str)  报告期
         report_type(str)  报告类型 1合并报表 2单季合并 3调整单季合并表 4调整合并报表 5调整前合并报表 6母公司报表 7母公司单季表 8 母公司调整单季表 9母公司调整表 10母公司调整前报表 11调整前合并报表 12母公司调整前报表
         comp_type(str)  公司类型(1一般工商业2银行3保险4证券)
         end_type(str)  报告期类型
         basic_eps(float)  基本每股收益
         diluted_eps(float)  稀释每股收益
         total_revenue(float)  营业总收入
         revenue(float)  营业收入
         int_income(float)  利息收入
         prem_earned(float)  已赚保费
         comm_income(float)  手续费及佣金收入
         n_commis_income(float)  手续费及佣金净收入
         n_oth_income(float)  其他经营净收益
         n_oth_b_income(float)  加:其他业务净收益
         prem_income(float)  保险业务收入
         out_prem(float)  减:分出保费
         une_prem_reser(float)  提取未到期责任准备金
         reins_income(float)  其中:分保费收入
         n_sec_tb_income(float)  代理买卖证券业务净收入
         n_sec_uw_income(float)  证券承销业务净收入
         n_asset_mg_income(float)  受托客户资产管理业务净收入
         oth_b_income(float)  其他业务收入
         fv_value_chg_gain(float)  加:公允价值变动净收益
         invest_income(float)  加:投资净收益
         ass_invest_income(float)  其中:对联营企业和合营企业的投资收益
         forex_gain(float)  加:汇兑净收益
         total_cogs(float)  营业总成本
         oper_cost(float)  减:营业成本
         int_exp(float)  减:利息支出
         comm_exp(float)  减:手续费及佣金支出
         biz_tax_surchg(float)  减:营业税金及附加
         sell_exp(float)  减:销售费用
         admin_exp(float)  减:管理费用
         fin_exp(float)  减:财务费用
         assets_impair_loss(float)  减:资产减值损失
         prem_refund(float)  退保金
         compens_payout(float)  赔付总支出
         reser_insur_liab(float)  提取保险责任准备金
         div_payt(float)  保户红利支出
         reins_exp(float)  分保费用
         oper_exp(float)  营业支出
         compens_payout_refu(float)  减:摊回赔付支出
         insur_reser_refu(float)  减:摊回保险责任准备金
         reins_cost_refund(float)  减:摊回分保费用
         other_bus_cost(float)  其他业务成本
         operate_profit(float)  营业利润
         non_oper_income(float)  加:营业外收入
         non_oper_exp(float)  减:营业外支出
         nca_disploss(float)  其中:减:非流动资产处置净损失
         total_profit(float)  利润总额
         income_tax(float)  所得税费用
         n_income(float)  净利润(含少数股东损益)
         n_income_attr_p(float)  净利润(不含少数股东损益)
         minority_gain(float)  少数股东损益
         oth_compr_income(float)  其他综合收益
         t_compr_income(float)  综合收益总额
         compr_inc_attr_p(float)  归属于母公司(或股东)的综合收益总额
         compr_inc_attr_m_s(float)  归属于少数股东的综合收益总额
         ebit(float)  息税前利润
         ebitda(float)  息税折旧摊销前利润
         insurance_exp(float)  保险业务支出
         undist_profit(float)  年初未分配利润
         distable_profit(float)  可分配利润
         rd_exp(float)  研发费用
         fin_exp_int_exp(float)  财务费用:利息费用
         fin_exp_int_inc(float)  财务费用:利息收入
         transfer_surplus_rese(float)  盈余公积转入
         transfer_housing_imprest(float)  住房周转金转入
         transfer_oth(float)  其他转入
         adj_lossgain(float)  调整以前年度损益
         withdra_legal_surplus(float)  提取法定盈余公积
         withdra_legal_pubfund(float)  提取法定公益金
         withdra_biz_devfund(float)  提取企业发展基金
         withdra_rese_fund(float)  提取储备基金
         withdra_oth_ersu(float)  提取任意盈余公积金
         workers_welfare(float)  职工奖金福利
         distr_profit_shrhder(float)  可供股东分配的利润
         prfshare_payable_dvd(float)  应付优先股股利
         comshare_payable_dvd(float)  应付普通股股利
         capit_comstock_div(float)  转作股本的普通股股利
         net_after_nr_lp_correct(float)  扣除非经常性损益后的净利润（更正前）
         oth_income(float)  其他收益
         asset_disp_income(float)  资产处置收益
         continued_net_profit(float)  持续经营净利润
         end_net_profit(float)  终止经营净利润
         credit_impa_loss(float)  信用减值损失
         net_expo_hedging_benefits(float)  净敞口套期收益
         oth_impair_loss_assets(float)  其他资产减值损失
         total_opcost(float)  营业总成本2
         amodcost_fin_assets(float)  以摊余成本计量的金融资产终止确认收益
         update_flag(str)  更新标识
        
        """
        return super().query(fields, **kwargs)

    def process(self, process_type: ProcessType = ProcessType.INCREASE):
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
            "f_ann_date": "",
            "start_date": "",
            "end_date": "",
            "period": "",
            "report_type": "",
            "comp_type": "",
            "end_type": "",
            "is_calc": "",
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

        def fetch_save(offset_val=0):
            try:
                kwargs['offset'] = str(offset_val)
                self.logger.debug("Invoke pro.income_vip with args: {}".format(kwargs))
                res = self.tushare_query('income_vip', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_income_vip',
                           con=self.engine,
                           if_exists='append',
                           index=False,
                           index_label=['ts_code'])
                return res
            except Exception as err:
                raise ProcessException(kwargs, err)

        df = fetch_save(offset)
        offset += df.shape[0]
        while kwargs['limit'] != "" and str(df.shape[0]) == kwargs['limit']:
            df = fetch_save(offset)
            offset += df.shape[0]
        return offset - init_offset


setattr(IncomeVip, 'default_limit', default_limit_ext)
setattr(IncomeVip, 'default_cron_express', default_cron_express_ext)
setattr(IncomeVip, 'default_order_by', default_order_by_ext)
setattr(IncomeVip, 'prepare', prepare_ext)
setattr(IncomeVip, 'tushare_parameters', tushare_parameters_ext)
setattr(IncomeVip, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.income_vip())

    api = IncomeVip(config)
    api.process()    # 同步增量数据
    print(api.income_vip())    # 数据查询接口
