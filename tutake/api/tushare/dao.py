from importlib import import_module

from tutake.utils.singleton import Singleton


@Singleton
class DAO(object):

    def __init__(self):
        self.instances = {}
        pass

    def __getattr__(self, name):
        if not self.instances.get(name):
            self.instances[name] = self.instance_from_name(name)
        return self.instances.get(name)

    def instance_from_name(self, name):

        if name == 'adj_factor':
            adj_factor_module = import_module("tutake.api.tushare.adj_factor")
            clazz = getattr(adj_factor_module, "AdjFactor")
            return clazz()
        if name == 'stock_company':
            stock_company_module = import_module("tutake.api.tushare.stock_company")
            clazz = getattr(stock_company_module, "StockCompany")
            return clazz()
        if name == 'daily':
            daily_module = import_module("tutake.api.tushare.daily")
            clazz = getattr(daily_module, "Daily")
            return clazz()
        if name == 'moneyflow':
            moneyflow_module = import_module("tutake.api.tushare.moneyflow")
            clazz = getattr(moneyflow_module, "Moneyflow")
            return clazz()
        if name == 'bak_daily':
            bak_daily_module = import_module("tutake.api.tushare.bak_daily")
            clazz = getattr(bak_daily_module, "BakDaily")
            return clazz()
        if name == 'namechange':
            namechange_module = import_module("tutake.api.tushare.namechange")
            clazz = getattr(namechange_module, "Namechange")
            return clazz()
        if name == 'fund_basic':
            fund_basic_module = import_module("tutake.api.tushare.fund_basic")
            clazz = getattr(fund_basic_module, "FundBasic")
            return clazz()
        if name == 'monthly':
            monthly_module = import_module("tutake.api.tushare.monthly")
            clazz = getattr(monthly_module, "Monthly")
            return clazz()
        if name == 'moneyflow_hsgt':
            moneyflow_hsgt_module = import_module("tutake.api.tushare.moneyflow_hsgt")
            clazz = getattr(moneyflow_hsgt_module, "MoneyflowHsgt")
            return clazz()
        if name == 'stk_rewards':
            stk_rewards_module = import_module("tutake.api.tushare.stk_rewards")
            clazz = getattr(stk_rewards_module, "StkRewards")
            return clazz()
        if name == 'hs_const':
            hs_const_module = import_module("tutake.api.tushare.hs_const")
            clazz = getattr(hs_const_module, "HsConst")
            return clazz()
        if name == 'bak_basic':
            bak_basic_module = import_module("tutake.api.tushare.bak_basic")
            clazz = getattr(bak_basic_module, "BakBasic")
            return clazz()
        if name == 'suspend_d':
            suspend_d_module = import_module("tutake.api.tushare.suspend_d")
            clazz = getattr(suspend_d_module, "SuspendD")
            return clazz()
        if name == 'weekly':
            weekly_module = import_module("tutake.api.tushare.weekly")
            clazz = getattr(weekly_module, "Weekly")
            return clazz()
        if name == 'stock_basic':
            stock_basic_module = import_module("tutake.api.tushare.stock_basic")
            clazz = getattr(stock_basic_module, "StockBasic")
            return clazz()
        if name == 'new_share':
            new_share_module = import_module("tutake.api.tushare.new_share")
            clazz = getattr(new_share_module, "NewShare")
            return clazz()
        if name == 'stk_managers':
            stk_managers_module = import_module("tutake.api.tushare.stk_managers")
            clazz = getattr(stk_managers_module, "StkManagers")
            return clazz()
        if name == 'ggt_daily':
            ggt_daily_module = import_module("tutake.api.tushare.ggt_daily")
            clazz = getattr(ggt_daily_module, "GgtDaily")
            return clazz()
        if name == 'ggt_top10':
            ggt_top10_module = import_module("tutake.api.tushare.ggt_top10")
            clazz = getattr(ggt_top10_module, "GgtTop10")
            return clazz()
        if name == 'hsgt_top10':
            hsgt_top10_module = import_module("tutake.api.tushare.hsgt_top10")
            clazz = getattr(hsgt_top10_module, "HsgtTop10")
            return clazz()
        if name == 'ggt_monthly':
            ggt_monthly_module = import_module("tutake.api.tushare.ggt_monthly")
            clazz = getattr(ggt_monthly_module, "GgtMonthly")
            return clazz()
        if name == 'income_vip':
            income_vip_module = import_module("tutake.api.tushare.income_vip")
            clazz = getattr(income_vip_module, "IncomeVip")
            return clazz()
        if name == 'index_basic':
            index_basic_module = import_module("tutake.api.tushare.index_basic")
            clazz = getattr(index_basic_module, "IndexBasic")
            return clazz()
