"""
This file is auto generator by CodeGenerator. Don't modify it directly, instead alter tushare_api.tmpl of it.

Tushare balancesheet_vip接口
获取上市公司资产负债表
数据接口-沪深股票-财务数据-资产负债表  https://tushare.pro/document/2?doc_id=36

@author: rmfish
"""
import pandas as pd
import tushare as ts
from sqlalchemy import Integer, String, Float, Column, create_engine
from sqlalchemy.orm import sessionmaker

from tutake.api.process import DataProcess
from tutake.api.process_report import ProcessException
from tutake.api.tushare.balancesheet_vip_ext import *
from tutake.api.tushare.base_dao import BaseDao, Base
from tutake.api.tushare.dao import DAO
from tutake.api.tushare.tushare_base import TuShareBase
from tutake.utils.config import TutakeConfig
from tutake.utils.utils import project_root


class TushareBalancesheetVip(Base):
    __tablename__ = "tushare_balancesheet_vip"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts_code = Column(String, index=True, comment='TS股票代码')
    ann_date = Column(String, index=True, comment='公告日期')
    f_ann_date = Column(String, index=True, comment='实际公告日期')
    end_date = Column(String, index=True, comment='报告期')
    report_type = Column(String, index=True, comment='报表类型')
    comp_type = Column(String, index=True, comment='公司类型(1一般工商业2银行3保险4证券)')
    end_type = Column(String, index=True, comment='报告期类型')
    total_share = Column(Float, comment='期末总股本')
    cap_rese = Column(Float, comment='资本公积金')
    undistr_porfit = Column(Float, comment='未分配利润')
    surplus_rese = Column(Float, comment='盈余公积金')
    special_rese = Column(Float, comment='专项储备')
    money_cap = Column(Float, comment='货币资金')
    trad_asset = Column(Float, comment='交易性金融资产')
    notes_receiv = Column(Float, comment='应收票据')
    accounts_receiv = Column(Float, comment='应收账款')
    oth_receiv = Column(Float, comment='其他应收款')
    prepayment = Column(Float, comment='预付款项')
    div_receiv = Column(Float, comment='应收股利')
    int_receiv = Column(Float, comment='应收利息')
    inventories = Column(Float, comment='存货')
    amor_exp = Column(Float, comment='长期待摊费用')
    nca_within_1y = Column(Float, comment='一年内到期的非流动资产')
    sett_rsrv = Column(Float, comment='结算备付金')
    loanto_oth_bank_fi = Column(Float, comment='拆出资金')
    premium_receiv = Column(Float, comment='应收保费')
    reinsur_receiv = Column(Float, comment='应收分保账款')
    reinsur_res_receiv = Column(Float, comment='应收分保合同准备金')
    pur_resale_fa = Column(Float, comment='买入返售金融资产')
    oth_cur_assets = Column(Float, comment='其他流动资产')
    total_cur_assets = Column(Float, comment='流动资产合计')
    fa_avail_for_sale = Column(Float, comment='可供出售金融资产')
    htm_invest = Column(Float, comment='持有至到期投资')
    lt_eqt_invest = Column(Float, comment='长期股权投资')
    invest_real_estate = Column(Float, comment='投资性房地产')
    time_deposits = Column(Float, comment='定期存款')
    oth_assets = Column(Float, comment='其他资产')
    lt_rec = Column(Float, comment='长期应收款')
    fix_assets = Column(Float, comment='固定资产')
    cip = Column(Float, comment='在建工程')
    const_materials = Column(Float, comment='工程物资')
    fixed_assets_disp = Column(Float, comment='固定资产清理')
    produc_bio_assets = Column(Float, comment='生产性生物资产')
    oil_and_gas_assets = Column(Float, comment='油气资产')
    intan_assets = Column(Float, comment='无形资产')
    r_and_d = Column(Float, comment='研发支出')
    goodwill = Column(Float, comment='商誉')
    lt_amor_exp = Column(Float, comment='长期待摊费用')
    defer_tax_assets = Column(Float, comment='递延所得税资产')
    decr_in_disbur = Column(Float, comment='发放贷款及垫款')
    oth_nca = Column(Float, comment='其他非流动资产')
    total_nca = Column(Float, comment='非流动资产合计')
    cash_reser_cb = Column(Float, comment='现金及存放中央银行款项')
    depos_in_oth_bfi = Column(Float, comment='存放同业和其它金融机构款项')
    prec_metals = Column(Float, comment='贵金属')
    deriv_assets = Column(Float, comment='衍生金融资产')
    rr_reins_une_prem = Column(Float, comment='应收分保未到期责任准备金')
    rr_reins_outstd_cla = Column(Float, comment='应收分保未决赔款准备金')
    rr_reins_lins_liab = Column(Float, comment='应收分保寿险责任准备金')
    rr_reins_lthins_liab = Column(Float, comment='应收分保长期健康险责任准备金')
    refund_depos = Column(Float, comment='存出保证金')
    ph_pledge_loans = Column(Float, comment='保户质押贷款')
    refund_cap_depos = Column(Float, comment='存出资本保证金')
    indep_acct_assets = Column(Float, comment='独立账户资产')
    client_depos = Column(Float, comment='其中：客户资金存款')
    client_prov = Column(Float, comment='其中：客户备付金')
    transac_seat_fee = Column(Float, comment='其中:交易席位费')
    invest_as_receiv = Column(Float, comment='应收款项类投资')
    total_assets = Column(Float, comment='资产总计')
    lt_borr = Column(Float, comment='长期借款')
    st_borr = Column(Float, comment='短期借款')
    cb_borr = Column(Float, comment='向中央银行借款')
    depos_ib_deposits = Column(Float, comment='吸收存款及同业存放')
    loan_oth_bank = Column(Float, comment='拆入资金')
    trading_fl = Column(Float, comment='交易性金融负债')
    notes_payable = Column(Float, comment='应付票据')
    acct_payable = Column(Float, comment='应付账款')
    adv_receipts = Column(Float, comment='预收款项')
    sold_for_repur_fa = Column(Float, comment='卖出回购金融资产款')
    comm_payable = Column(Float, comment='应付手续费及佣金')
    payroll_payable = Column(Float, comment='应付职工薪酬')
    taxes_payable = Column(Float, comment='应交税费')
    int_payable = Column(Float, comment='应付利息')
    div_payable = Column(Float, comment='应付股利')
    oth_payable = Column(Float, comment='其他应付款')
    acc_exp = Column(Float, comment='预提费用')
    deferred_inc = Column(Float, comment='递延收益')
    st_bonds_payable = Column(Float, comment='应付短期债券')
    payable_to_reinsurer = Column(Float, comment='应付分保账款')
    rsrv_insur_cont = Column(Float, comment='保险合同准备金')
    acting_trading_sec = Column(Float, comment='代理买卖证券款')
    acting_uw_sec = Column(Float, comment='代理承销证券款')
    non_cur_liab_due_1y = Column(Float, comment='一年内到期的非流动负债')
    oth_cur_liab = Column(Float, comment='其他流动负债')
    total_cur_liab = Column(Float, comment='流动负债合计')
    bond_payable = Column(Float, comment='应付债券')
    lt_payable = Column(Float, comment='长期应付款')
    specific_payables = Column(Float, comment='专项应付款')
    estimated_liab = Column(Float, comment='预计负债')
    defer_tax_liab = Column(Float, comment='递延所得税负债')
    defer_inc_non_cur_liab = Column(Float, comment='递延收益-非流动负债')
    oth_ncl = Column(Float, comment='其他非流动负债')
    total_ncl = Column(Float, comment='非流动负债合计')
    depos_oth_bfi = Column(Float, comment='同业和其它金融机构存放款项')
    deriv_liab = Column(Float, comment='衍生金融负债')
    depos = Column(Float, comment='吸收存款')
    agency_bus_liab = Column(Float, comment='代理业务负债')
    oth_liab = Column(Float, comment='其他负债')
    prem_receiv_adva = Column(Float, comment='预收保费')
    depos_received = Column(Float, comment='存入保证金')
    ph_invest = Column(Float, comment='保户储金及投资款')
    reser_une_prem = Column(Float, comment='未到期责任准备金')
    reser_outstd_claims = Column(Float, comment='未决赔款准备金')
    reser_lins_liab = Column(Float, comment='寿险责任准备金')
    reser_lthins_liab = Column(Float, comment='长期健康险责任准备金')
    indept_acc_liab = Column(Float, comment='独立账户负债')
    pledge_borr = Column(Float, comment='其中:质押借款')
    indem_payable = Column(Float, comment='应付赔付款')
    policy_div_payable = Column(Float, comment='应付保单红利')
    total_liab = Column(Float, comment='负债合计')
    treasury_share = Column(Float, comment='减:库存股')
    ordin_risk_reser = Column(Float, comment='一般风险准备')
    forex_differ = Column(Float, comment='外币报表折算差额')
    invest_loss_unconf = Column(Float, comment='未确认的投资损失')
    minority_int = Column(Float, comment='少数股东权益')
    total_hldr_eqy_exc_min_int = Column(Float, comment='股东权益合计(不含少数股东权益)')
    total_hldr_eqy_inc_min_int = Column(Float, comment='股东权益合计(含少数股东权益)')
    total_liab_hldr_eqy = Column(Float, comment='负债及股东权益总计')
    lt_payroll_payable = Column(Float, comment='长期应付职工薪酬')
    oth_comp_income = Column(Float, comment='其他综合收益')
    oth_eqt_tools = Column(Float, comment='其他权益工具')
    oth_eqt_tools_p_shr = Column(Float, comment='其他权益工具(优先股)')
    lending_funds = Column(Float, comment='融出资金')
    acc_receivable = Column(Float, comment='应收款项')
    st_fin_payable = Column(Float, comment='应付短期融资款')
    payables = Column(Float, comment='应付款项')
    hfs_assets = Column(Float, comment='持有待售的资产')
    hfs_sales = Column(Float, comment='持有待售的负债')
    cost_fin_assets = Column(Float, comment='以摊余成本计量的金融资产')
    fair_value_fin_assets = Column(Float, comment='以公允价值计量且其变动计入其他综合收益的金融资产')
    contract_assets = Column(Float, comment='合同资产')
    contract_liab = Column(Float, comment='合同负债')
    accounts_receiv_bill = Column(Float, comment='应收票据及应收账款')
    accounts_pay = Column(Float, comment='应付票据及应付账款')
    oth_rcv_total = Column(Float, comment='其他应收款(合计)（元）')
    fix_assets_total = Column(Float, comment='固定资产(合计)(元)')
    cip_total = Column(Float, comment='在建工程(合计)(元)')
    oth_pay_total = Column(Float, comment='其他应付款(合计)(元)')
    long_pay_total = Column(Float, comment='长期应付款(合计)(元)')
    debt_invest = Column(Float, comment='债权投资(元)')
    oth_debt_invest = Column(Float, comment='其他债权投资(元)')
    oth_eq_invest = Column(Float, comment='其他权益工具投资(元)')
    oth_illiq_fin_assets = Column(Float, comment='其他非流动金融资产(元)')
    oth_eq_ppbond = Column(Float, comment='其他权益工具:永续债(元)')
    receiv_financing = Column(Float, comment='应收款项融资')
    use_right_assets = Column(Float, comment='使用权资产')
    lease_liab = Column(Float, comment='租赁负债')
    update_flag = Column(String, comment='更新标识')


class BalancesheetVip(BaseDao, TuShareBase, DataProcess):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.engine = create_engine("%s/%s" % (config.get_data_sqlite_driver_url(), 'tushare_balancesheet_vip.db'),
                                    connect_args={'check_same_thread': False})
        session_factory = sessionmaker()
        session_factory.configure(bind=self.engine)
        TushareBalancesheetVip.__table__.create(bind=self.engine, checkfirst=True)

        query_fields = [
            'ts_code', 'ann_date', 'f_ann_date', 'start_date', 'end_date', 'period', 'report_type', 'comp_type',
            'end_type', 'end_type', 'limit', 'offset'
        ]
        entity_fields = [
            "ts_code", "ann_date", "f_ann_date", "end_date", "report_type", "comp_type", "end_type", "total_share",
            "cap_rese", "undistr_porfit", "surplus_rese", "special_rese", "money_cap", "trad_asset", "notes_receiv",
            "accounts_receiv", "oth_receiv", "prepayment", "div_receiv", "int_receiv", "inventories", "amor_exp",
            "nca_within_1y", "sett_rsrv", "loanto_oth_bank_fi", "premium_receiv", "reinsur_receiv",
            "reinsur_res_receiv", "pur_resale_fa", "oth_cur_assets", "total_cur_assets", "fa_avail_for_sale",
            "htm_invest", "lt_eqt_invest", "invest_real_estate", "time_deposits", "oth_assets", "lt_rec", "fix_assets",
            "cip", "const_materials", "fixed_assets_disp", "produc_bio_assets", "oil_and_gas_assets", "intan_assets",
            "r_and_d", "goodwill", "lt_amor_exp", "defer_tax_assets", "decr_in_disbur", "oth_nca", "total_nca",
            "cash_reser_cb", "depos_in_oth_bfi", "prec_metals", "deriv_assets", "rr_reins_une_prem",
            "rr_reins_outstd_cla", "rr_reins_lins_liab", "rr_reins_lthins_liab", "refund_depos", "ph_pledge_loans",
            "refund_cap_depos", "indep_acct_assets", "client_depos", "client_prov", "transac_seat_fee",
            "invest_as_receiv", "total_assets", "lt_borr", "st_borr", "cb_borr", "depos_ib_deposits", "loan_oth_bank",
            "trading_fl", "notes_payable", "acct_payable", "adv_receipts", "sold_for_repur_fa", "comm_payable",
            "payroll_payable", "taxes_payable", "int_payable", "div_payable", "oth_payable", "acc_exp", "deferred_inc",
            "st_bonds_payable", "payable_to_reinsurer", "rsrv_insur_cont", "acting_trading_sec", "acting_uw_sec",
            "non_cur_liab_due_1y", "oth_cur_liab", "total_cur_liab", "bond_payable", "lt_payable", "specific_payables",
            "estimated_liab", "defer_tax_liab", "defer_inc_non_cur_liab", "oth_ncl", "total_ncl", "depos_oth_bfi",
            "deriv_liab", "depos", "agency_bus_liab", "oth_liab", "prem_receiv_adva", "depos_received", "ph_invest",
            "reser_une_prem", "reser_outstd_claims", "reser_lins_liab", "reser_lthins_liab", "indept_acc_liab",
            "pledge_borr", "indem_payable", "policy_div_payable", "total_liab", "treasury_share", "ordin_risk_reser",
            "forex_differ", "invest_loss_unconf", "minority_int", "total_hldr_eqy_exc_min_int",
            "total_hldr_eqy_inc_min_int", "total_liab_hldr_eqy", "lt_payroll_payable", "oth_comp_income",
            "oth_eqt_tools", "oth_eqt_tools_p_shr", "lending_funds", "acc_receivable", "st_fin_payable", "payables",
            "hfs_assets", "hfs_sales", "cost_fin_assets", "fair_value_fin_assets", "contract_assets", "contract_liab",
            "accounts_receiv_bill", "accounts_pay", "oth_rcv_total", "fix_assets_total", "cip_total", "oth_pay_total",
            "long_pay_total", "debt_invest", "oth_debt_invest", "oth_eq_invest", "oth_illiq_fin_assets",
            "oth_eq_ppbond", "receiv_financing", "use_right_assets", "lease_liab", "update_flag"
        ]
        BaseDao.__init__(self, self.engine, session_factory, TushareBalancesheetVip, 'tushare_balancesheet_vip',
                         query_fields, entity_fields)
        DataProcess.__init__(self, "balancesheet_vip", config)
        TuShareBase.__init__(self, "balancesheet_vip", config, 5000)
        self.dao = DAO(config)

    def balancesheet_vip(self, fields='', **kwargs):
        """
        获取上市公司资产负债表
        | Arguments:
        | ts_code(str): required  股票代码
        | ann_date(str):   公告日期
        | f_ann_date(str):   实际公告日期
        | start_date(str):   报告期开始日期
        | end_date(str):   报告期结束日期
        | period(str):   报告期
        | report_type(str):   报告类型
        | comp_type(str):   公司类型
        | end_type(str):   报告期类型
        | end_type(str):   报告期编号 1~4报告期
        | limit(int):   单次返回数据长度
        | offset(int):   请求数据的开始位移量
        
        :return: DataFrame
         ts_code(str)  TS股票代码
         ann_date(str)  公告日期
         f_ann_date(str)  实际公告日期
         end_date(str)  报告期
         report_type(str)  报表类型
         comp_type(str)  公司类型(1一般工商业2银行3保险4证券)
         end_type(str)  报告期类型
         total_share(float)  期末总股本
         cap_rese(float)  资本公积金
         undistr_porfit(float)  未分配利润
         surplus_rese(float)  盈余公积金
         special_rese(float)  专项储备
         money_cap(float)  货币资金
         trad_asset(float)  交易性金融资产
         notes_receiv(float)  应收票据
         accounts_receiv(float)  应收账款
         oth_receiv(float)  其他应收款
         prepayment(float)  预付款项
         div_receiv(float)  应收股利
         int_receiv(float)  应收利息
         inventories(float)  存货
         amor_exp(float)  长期待摊费用
         nca_within_1y(float)  一年内到期的非流动资产
         sett_rsrv(float)  结算备付金
         loanto_oth_bank_fi(float)  拆出资金
         premium_receiv(float)  应收保费
         reinsur_receiv(float)  应收分保账款
         reinsur_res_receiv(float)  应收分保合同准备金
         pur_resale_fa(float)  买入返售金融资产
         oth_cur_assets(float)  其他流动资产
         total_cur_assets(float)  流动资产合计
         fa_avail_for_sale(float)  可供出售金融资产
         htm_invest(float)  持有至到期投资
         lt_eqt_invest(float)  长期股权投资
         invest_real_estate(float)  投资性房地产
         time_deposits(float)  定期存款
         oth_assets(float)  其他资产
         lt_rec(float)  长期应收款
         fix_assets(float)  固定资产
         cip(float)  在建工程
         const_materials(float)  工程物资
         fixed_assets_disp(float)  固定资产清理
         produc_bio_assets(float)  生产性生物资产
         oil_and_gas_assets(float)  油气资产
         intan_assets(float)  无形资产
         r_and_d(float)  研发支出
         goodwill(float)  商誉
         lt_amor_exp(float)  长期待摊费用
         defer_tax_assets(float)  递延所得税资产
         decr_in_disbur(float)  发放贷款及垫款
         oth_nca(float)  其他非流动资产
         total_nca(float)  非流动资产合计
         cash_reser_cb(float)  现金及存放中央银行款项
         depos_in_oth_bfi(float)  存放同业和其它金融机构款项
         prec_metals(float)  贵金属
         deriv_assets(float)  衍生金融资产
         rr_reins_une_prem(float)  应收分保未到期责任准备金
         rr_reins_outstd_cla(float)  应收分保未决赔款准备金
         rr_reins_lins_liab(float)  应收分保寿险责任准备金
         rr_reins_lthins_liab(float)  应收分保长期健康险责任准备金
         refund_depos(float)  存出保证金
         ph_pledge_loans(float)  保户质押贷款
         refund_cap_depos(float)  存出资本保证金
         indep_acct_assets(float)  独立账户资产
         client_depos(float)  其中：客户资金存款
         client_prov(float)  其中：客户备付金
         transac_seat_fee(float)  其中:交易席位费
         invest_as_receiv(float)  应收款项类投资
         total_assets(float)  资产总计
         lt_borr(float)  长期借款
         st_borr(float)  短期借款
         cb_borr(float)  向中央银行借款
         depos_ib_deposits(float)  吸收存款及同业存放
         loan_oth_bank(float)  拆入资金
         trading_fl(float)  交易性金融负债
         notes_payable(float)  应付票据
         acct_payable(float)  应付账款
         adv_receipts(float)  预收款项
         sold_for_repur_fa(float)  卖出回购金融资产款
         comm_payable(float)  应付手续费及佣金
         payroll_payable(float)  应付职工薪酬
         taxes_payable(float)  应交税费
         int_payable(float)  应付利息
         div_payable(float)  应付股利
         oth_payable(float)  其他应付款
         acc_exp(float)  预提费用
         deferred_inc(float)  递延收益
         st_bonds_payable(float)  应付短期债券
         payable_to_reinsurer(float)  应付分保账款
         rsrv_insur_cont(float)  保险合同准备金
         acting_trading_sec(float)  代理买卖证券款
         acting_uw_sec(float)  代理承销证券款
         non_cur_liab_due_1y(float)  一年内到期的非流动负债
         oth_cur_liab(float)  其他流动负债
         total_cur_liab(float)  流动负债合计
         bond_payable(float)  应付债券
         lt_payable(float)  长期应付款
         specific_payables(float)  专项应付款
         estimated_liab(float)  预计负债
         defer_tax_liab(float)  递延所得税负债
         defer_inc_non_cur_liab(float)  递延收益-非流动负债
         oth_ncl(float)  其他非流动负债
         total_ncl(float)  非流动负债合计
         depos_oth_bfi(float)  同业和其它金融机构存放款项
         deriv_liab(float)  衍生金融负债
         depos(float)  吸收存款
         agency_bus_liab(float)  代理业务负债
         oth_liab(float)  其他负债
         prem_receiv_adva(float)  预收保费
         depos_received(float)  存入保证金
         ph_invest(float)  保户储金及投资款
         reser_une_prem(float)  未到期责任准备金
         reser_outstd_claims(float)  未决赔款准备金
         reser_lins_liab(float)  寿险责任准备金
         reser_lthins_liab(float)  长期健康险责任准备金
         indept_acc_liab(float)  独立账户负债
         pledge_borr(float)  其中:质押借款
         indem_payable(float)  应付赔付款
         policy_div_payable(float)  应付保单红利
         total_liab(float)  负债合计
         treasury_share(float)  减:库存股
         ordin_risk_reser(float)  一般风险准备
         forex_differ(float)  外币报表折算差额
         invest_loss_unconf(float)  未确认的投资损失
         minority_int(float)  少数股东权益
         total_hldr_eqy_exc_min_int(float)  股东权益合计(不含少数股东权益)
         total_hldr_eqy_inc_min_int(float)  股东权益合计(含少数股东权益)
         total_liab_hldr_eqy(float)  负债及股东权益总计
         lt_payroll_payable(float)  长期应付职工薪酬
         oth_comp_income(float)  其他综合收益
         oth_eqt_tools(float)  其他权益工具
         oth_eqt_tools_p_shr(float)  其他权益工具(优先股)
         lending_funds(float)  融出资金
         acc_receivable(float)  应收款项
         st_fin_payable(float)  应付短期融资款
         payables(float)  应付款项
         hfs_assets(float)  持有待售的资产
         hfs_sales(float)  持有待售的负债
         cost_fin_assets(float)  以摊余成本计量的金融资产
         fair_value_fin_assets(float)  以公允价值计量且其变动计入其他综合收益的金融资产
         contract_assets(float)  合同资产
         contract_liab(float)  合同负债
         accounts_receiv_bill(float)  应收票据及应收账款
         accounts_pay(float)  应付票据及应付账款
         oth_rcv_total(float)  其他应收款(合计)（元）
         fix_assets_total(float)  固定资产(合计)(元)
         cip_total(float)  在建工程(合计)(元)
         oth_pay_total(float)  其他应付款(合计)(元)
         long_pay_total(float)  长期应付款(合计)(元)
         debt_invest(float)  债权投资(元)
         oth_debt_invest(float)  其他债权投资(元)
         oth_eq_invest(float)  其他权益工具投资(元)
         oth_illiq_fin_assets(float)  其他非流动金融资产(元)
         oth_eq_ppbond(float)  其他权益工具:永续债(元)
         receiv_financing(float)  应收款项融资
         use_right_assets(float)  使用权资产
         lease_liab(float)  租赁负债
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
            "end_type": "",
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
                self.logger.debug("Invoke pro.balancesheet_vip with args: {}".format(kwargs))
                res = self.tushare_query('balancesheet_vip', fields=self.entity_fields, **kwargs)
                res.to_sql('tushare_balancesheet_vip',
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


setattr(BalancesheetVip, 'default_limit', default_limit_ext)
setattr(BalancesheetVip, 'default_cron_express', default_cron_express_ext)
setattr(BalancesheetVip, 'default_order_by', default_order_by_ext)
setattr(BalancesheetVip, 'prepare', prepare_ext)
setattr(BalancesheetVip, 'tushare_parameters', tushare_parameters_ext)
setattr(BalancesheetVip, 'param_loop_process', param_loop_process_ext)

if __name__ == '__main__':
    pd.set_option('display.max_columns', 50)    # 显示列数
    pd.set_option('display.width', 100)
    config = TutakeConfig(project_root())
    pro = ts.pro_api(config.get_tushare_token())
    print(pro.balancesheet_vip())

    api = BalancesheetVip(config)
    api.process()    # 同步增量数据
    print(api.balancesheet_vip())    # 数据查询接口
