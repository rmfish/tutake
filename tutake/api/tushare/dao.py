from importlib import import_module


class Singleton(object):

    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]


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

        if name == 'fund_basic':
            fund_basic_module = import_module("tutake.api.tushare.fund_basic")
            clazz = getattr(fund_basic_module, "FundBasic")
            return clazz()
        if name == 'stock_basic':
            stock_basic_module = import_module("tutake.api.tushare.stock_basic")
            clazz = getattr(stock_basic_module, "StockBasic")
            return clazz()
        if name == 'trade_cal':
            trade_cal_module = import_module("tutake.api.tushare.trade_cal")
            clazz = getattr(trade_cal_module, "TradeCal")
            return clazz()
        if name == 'daily':
            daily_module = import_module("tutake.api.tushare.daily")
            clazz = getattr(daily_module, "Daily")
            return clazz()
        if name == 'adj_factor':
            adj_factor_module = import_module("tutake.api.tushare.adj_factor")
            clazz = getattr(adj_factor_module, "AdjFactor")
            return clazz()
        if name == 'namechange':
            namechange_module = import_module("tutake.api.tushare.namechange")
            clazz = getattr(namechange_module, "Namechange")
            return clazz()
        if name == 'hs_const':
            hs_const_module = import_module("tutake.api.tushare.hs_const")
            clazz = getattr(hs_const_module, "HsConst")
            return clazz()
        if name == 'stock_company':
            stock_company_module = import_module("tutake.api.tushare.stock_company")
            clazz = getattr(stock_company_module, "StockCompany")
            return clazz()
        if name == 'new_share':
            new_share_module = import_module("tutake.api.tushare.new_share")
            clazz = getattr(new_share_module, "NewShare")
            return clazz()
        if name == 'weekly':
            weekly_module = import_module("tutake.api.tushare.weekly")
            clazz = getattr(weekly_module, "Weekly")
            return clazz()
        if name == 'monthly':
            monthly_module = import_module("tutake.api.tushare.monthly")
            clazz = getattr(monthly_module, "Monthly")
            return clazz()
        if name == 'stk_managers':
            stk_managers_module = import_module("tutake.api.tushare.stk_managers")
            clazz = getattr(stk_managers_module, "StkManagers")
            return clazz()
        if name == 'stk_rewards':
            stk_rewards_module = import_module("tutake.api.tushare.stk_rewards")
            clazz = getattr(stk_rewards_module, "StkRewards")
            return clazz()
        if name == 'suspend_d':
            suspend_d_module = import_module("tutake.api.tushare.suspend_d")
            clazz = getattr(suspend_d_module, "SuspendD")
            return clazz()
        if name == 'bak_daily':
            bak_daily_module = import_module("tutake.api.tushare.bak_daily")
            clazz = getattr(bak_daily_module, "BakDaily")
            return clazz()
        if name == 'bak_basic':
            bak_basic_module = import_module("tutake.api.tushare.bak_basic")
            clazz = getattr(bak_basic_module, "BakBasic")
            return clazz()
        if name == 'index_basic':
            index_basic_module = import_module("tutake.api.tushare.index_basic")
            clazz = getattr(index_basic_module, "IndexBasic")
            return clazz()


if __name__ == '__main__':
    dao1 = DAO()
    print(dao1.stock_basic.count())
