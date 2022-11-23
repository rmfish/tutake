from importlib import import_module

from tutake.utils.singleton import Singleton


@Singleton
class DAO(object):

    def __init__(self):
        self.instances = {}
        pass

    def __getattr__(self, name, config):
        if not self.instances.get(name):
            self.instances[name] = self.instance_from_name(name, config)
        return self.instances.get(name)

    def all_apis(self):
        return [
            'adj_factor', 'stock_company', 'daily', 'moneyflow', 'bak_daily', 'namechange', 'fund_basic', 'monthly',
            'moneyflow_hsgt', 'stk_rewards', 'hs_const', 'bak_basic', 'suspend_d', 'weekly', 'stock_basic', 'new_share',
            'stk_managers', 'ggt_daily', 'ggt_top10', 'hsgt_top10', 'ggt_monthly', 'income_vip', 'balancesheet_vip',
            'cashflow_vip', 'forecast_vip', 'express_vip', 'dividend', 'fina_indicator_vip', 'index_daily',
            'index_dailybasic', 'index_classify', 'index_member', 'ths_index', 'ths_daily', 'ths_member',
            'index_global', 'anns', 'trade_cal', 'fund_adj', 'fund_company', 'fund_div', 'fund_manager', 'fund_nav',
            'fund_portfolio', 'fund_sales_ratio', 'fund_sales_vol', 'fund_share', 'fund_daily', 'index_basic'
        ]

    def instance_from_name(self, name, config):

        if name == 'adj_factor':
            adj_factor_module = import_module("tutake.api.tushare.adj_factor")
            clazz = getattr(adj_factor_module, "AdjFactor")
            return clazz(config)
        if name == 'stock_company':
            stock_company_module = import_module("tutake.api.tushare.stock_company")
            clazz = getattr(stock_company_module, "StockCompany")
            return clazz(config)
        if name == 'daily':
            daily_module = import_module("tutake.api.tushare.daily")
            clazz = getattr(daily_module, "Daily")
            return clazz(config)
        if name == 'moneyflow':
            moneyflow_module = import_module("tutake.api.tushare.moneyflow")
            clazz = getattr(moneyflow_module, "Moneyflow")
            return clazz(config)
        if name == 'bak_daily':
            bak_daily_module = import_module("tutake.api.tushare.bak_daily")
            clazz = getattr(bak_daily_module, "BakDaily")
            return clazz(config)
        if name == 'namechange':
            namechange_module = import_module("tutake.api.tushare.namechange")
            clazz = getattr(namechange_module, "Namechange")
            return clazz(config)
        if name == 'fund_basic':
            fund_basic_module = import_module("tutake.api.tushare.fund_basic")
            clazz = getattr(fund_basic_module, "FundBasic")
            return clazz(config)
        if name == 'monthly':
            monthly_module = import_module("tutake.api.tushare.monthly")
            clazz = getattr(monthly_module, "Monthly")
            return clazz(config)
        if name == 'moneyflow_hsgt':
            moneyflow_hsgt_module = import_module("tutake.api.tushare.moneyflow_hsgt")
            clazz = getattr(moneyflow_hsgt_module, "MoneyflowHsgt")
            return clazz(config)
        if name == 'stk_rewards':
            stk_rewards_module = import_module("tutake.api.tushare.stk_rewards")
            clazz = getattr(stk_rewards_module, "StkRewards")
            return clazz(config)
        if name == 'hs_const':
            hs_const_module = import_module("tutake.api.tushare.hs_const")
            clazz = getattr(hs_const_module, "HsConst")
            return clazz(config)
        if name == 'bak_basic':
            bak_basic_module = import_module("tutake.api.tushare.bak_basic")
            clazz = getattr(bak_basic_module, "BakBasic")
            return clazz(config)
        if name == 'suspend_d':
            suspend_d_module = import_module("tutake.api.tushare.suspend_d")
            clazz = getattr(suspend_d_module, "SuspendD")
            return clazz(config)
        if name == 'weekly':
            weekly_module = import_module("tutake.api.tushare.weekly")
            clazz = getattr(weekly_module, "Weekly")
            return clazz(config)
        if name == 'stock_basic':
            stock_basic_module = import_module("tutake.api.tushare.stock_basic")
            clazz = getattr(stock_basic_module, "StockBasic")
            return clazz(config)
        if name == 'new_share':
            new_share_module = import_module("tutake.api.tushare.new_share")
            clazz = getattr(new_share_module, "NewShare")
            return clazz(config)
        if name == 'stk_managers':
            stk_managers_module = import_module("tutake.api.tushare.stk_managers")
            clazz = getattr(stk_managers_module, "StkManagers")
            return clazz(config)
        if name == 'ggt_daily':
            ggt_daily_module = import_module("tutake.api.tushare.ggt_daily")
            clazz = getattr(ggt_daily_module, "GgtDaily")
            return clazz(config)
        if name == 'ggt_top10':
            ggt_top10_module = import_module("tutake.api.tushare.ggt_top10")
            clazz = getattr(ggt_top10_module, "GgtTop10")
            return clazz(config)
        if name == 'hsgt_top10':
            hsgt_top10_module = import_module("tutake.api.tushare.hsgt_top10")
            clazz = getattr(hsgt_top10_module, "HsgtTop10")
            return clazz(config)
        if name == 'ggt_monthly':
            ggt_monthly_module = import_module("tutake.api.tushare.ggt_monthly")
            clazz = getattr(ggt_monthly_module, "GgtMonthly")
            return clazz(config)
        if name == 'income_vip':
            income_vip_module = import_module("tutake.api.tushare.income_vip")
            clazz = getattr(income_vip_module, "IncomeVip")
            return clazz(config)
        if name == 'balancesheet_vip':
            balancesheet_vip_module = import_module("tutake.api.tushare.balancesheet_vip")
            clazz = getattr(balancesheet_vip_module, "BalancesheetVip")
            return clazz(config)
        if name == 'cashflow_vip':
            cashflow_vip_module = import_module("tutake.api.tushare.cashflow_vip")
            clazz = getattr(cashflow_vip_module, "CashflowVip")
            return clazz(config)
        if name == 'forecast_vip':
            forecast_vip_module = import_module("tutake.api.tushare.forecast_vip")
            clazz = getattr(forecast_vip_module, "ForecastVip")
            return clazz(config)
        if name == 'express_vip':
            express_vip_module = import_module("tutake.api.tushare.express_vip")
            clazz = getattr(express_vip_module, "ExpressVip")
            return clazz(config)
        if name == 'dividend':
            dividend_module = import_module("tutake.api.tushare.dividend")
            clazz = getattr(dividend_module, "Dividend")
            return clazz(config)
        if name == 'fina_indicator_vip':
            fina_indicator_vip_module = import_module("tutake.api.tushare.fina_indicator_vip")
            clazz = getattr(fina_indicator_vip_module, "FinaIndicatorVip")
            return clazz(config)
        if name == 'index_daily':
            index_daily_module = import_module("tutake.api.tushare.index_daily")
            clazz = getattr(index_daily_module, "IndexDaily")
            return clazz(config)
        if name == 'index_dailybasic':
            index_dailybasic_module = import_module("tutake.api.tushare.index_dailybasic")
            clazz = getattr(index_dailybasic_module, "IndexDailybasic")
            return clazz(config)
        if name == 'index_classify':
            index_classify_module = import_module("tutake.api.tushare.index_classify")
            clazz = getattr(index_classify_module, "IndexClassify")
            return clazz(config)
        if name == 'index_member':
            index_member_module = import_module("tutake.api.tushare.index_member")
            clazz = getattr(index_member_module, "IndexMember")
            return clazz(config)
        if name == 'ths_index':
            ths_index_module = import_module("tutake.api.tushare.ths_index")
            clazz = getattr(ths_index_module, "ThsIndex")
            return clazz(config)
        if name == 'ths_daily':
            ths_daily_module = import_module("tutake.api.tushare.ths_daily")
            clazz = getattr(ths_daily_module, "ThsDaily")
            return clazz(config)
        if name == 'ths_member':
            ths_member_module = import_module("tutake.api.tushare.ths_member")
            clazz = getattr(ths_member_module, "ThsMember")
            return clazz(config)
        if name == 'index_global':
            index_global_module = import_module("tutake.api.tushare.index_global")
            clazz = getattr(index_global_module, "IndexGlobal")
            return clazz(config)
        if name == 'anns':
            anns_module = import_module("tutake.api.tushare.anns")
            clazz = getattr(anns_module, "Anns")
            return clazz(config)
        if name == 'trade_cal':
            trade_cal_module = import_module("tutake.api.tushare.trade_cal")
            clazz = getattr(trade_cal_module, "TradeCal")
            return clazz(config)
        if name == 'fund_adj':
            fund_adj_module = import_module("tutake.api.tushare.fund_adj")
            clazz = getattr(fund_adj_module, "FundAdj")
            return clazz(config)
        if name == 'fund_company':
            fund_company_module = import_module("tutake.api.tushare.fund_company")
            clazz = getattr(fund_company_module, "FundCompany")
            return clazz(config)
        if name == 'fund_div':
            fund_div_module = import_module("tutake.api.tushare.fund_div")
            clazz = getattr(fund_div_module, "FundDiv")
            return clazz(config)
        if name == 'fund_manager':
            fund_manager_module = import_module("tutake.api.tushare.fund_manager")
            clazz = getattr(fund_manager_module, "FundManager")
            return clazz(config)
        if name == 'fund_nav':
            fund_nav_module = import_module("tutake.api.tushare.fund_nav")
            clazz = getattr(fund_nav_module, "FundNav")
            return clazz(config)
        if name == 'fund_portfolio':
            fund_portfolio_module = import_module("tutake.api.tushare.fund_portfolio")
            clazz = getattr(fund_portfolio_module, "FundPortfolio")
            return clazz(config)
        if name == 'fund_sales_ratio':
            fund_sales_ratio_module = import_module("tutake.api.tushare.fund_sales_ratio")
            clazz = getattr(fund_sales_ratio_module, "FundSalesRatio")
            return clazz(config)
        if name == 'fund_sales_vol':
            fund_sales_vol_module = import_module("tutake.api.tushare.fund_sales_vol")
            clazz = getattr(fund_sales_vol_module, "FundSalesVol")
            return clazz(config)
        if name == 'fund_share':
            fund_share_module = import_module("tutake.api.tushare.fund_share")
            clazz = getattr(fund_share_module, "FundShare")
            return clazz(config)
        if name == 'fund_daily':
            fund_daily_module = import_module("tutake.api.tushare.fund_daily")
            clazz = getattr(fund_daily_module, "FundDaily")
            return clazz(config)
        if name == 'index_basic':
            index_basic_module = import_module("tutake.api.tushare.index_basic")
            clazz = getattr(index_basic_module, "IndexBasic")
            return clazz(config)
        else:
            return None
