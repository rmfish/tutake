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
            self.instances[name] = self._init_dao(name)
        return self.instances.get(name)

    def _init_dao(self, name):

        if name == 'daily':
            daily_module = import_module("tutake.api.daily")
            clazz = getattr(daily_module, "Daily")
            return clazz()

        if name == 'adj_factor':
            adj_factor_module = import_module("tutake.api.adj_factor")
            clazz = getattr(adj_factor_module, "AdjFactor")
            return clazz()

        if name == 'suspend':
            suspend_module = import_module("tutake.api.suspend")
            clazz = getattr(suspend_module, "Suspend")
            return clazz()

        if name == 'daily_basic':
            daily_basic_module = import_module("tutake.api.daily_basic")
            clazz = getattr(daily_basic_module, "DailyBasic")
            return clazz()

        if name == 'moneyflow_hsgt':
            moneyflow_hsgt_module = import_module("tutake.api.moneyflow_hsgt")
            clazz = getattr(moneyflow_hsgt_module, "MoneyflowHsgt")
            return clazz()

        if name == 'hsgt_top10':
            hsgt_top10_module = import_module("tutake.api.hsgt_top10")
            clazz = getattr(hsgt_top10_module, "HsgtTop10")
            return clazz()

        if name == 'ggt_top10':
            ggt_top10_module = import_module("tutake.api.ggt_top10")
            clazz = getattr(ggt_top10_module, "GgtTop10")
            return clazz()

        if name == 'None':
            None_module = import_module("tutake.api.None")
            clazz = getattr(None_module, "")
            return clazz()

        if name == 'weekly':
            weekly_module = import_module("tutake.api.weekly")
            clazz = getattr(weekly_module, "Weekly")
            return clazz()

        if name == 'monthly':
            monthly_module = import_module("tutake.api.monthly")
            clazz = getattr(monthly_module, "Monthly")
            return clazz()

        if name == 'None':
            None_module = import_module("tutake.api.None")
            clazz = getattr(None_module, "")
            return clazz()

        if name == 'moneyflow':
            moneyflow_module = import_module("tutake.api.moneyflow")
            clazz = getattr(moneyflow_module, "Moneyflow")
            return clazz()

        if name == 'stk_limit':
            stk_limit_module = import_module("tutake.api.stk_limit")
            clazz = getattr(stk_limit_module, "StkLimit")
            return clazz()

        if name == 'ggt_daily':
            ggt_daily_module = import_module("tutake.api.ggt_daily")
            clazz = getattr(ggt_daily_module, "GgtDaily")
            return clazz()

        if name == 'ggt_monthly':
            ggt_monthly_module = import_module("tutake.api.ggt_monthly")
            clazz = getattr(ggt_monthly_module, "GgtMonthly")
            return clazz()

        if name == 'suspend_d':
            suspend_d_module = import_module("tutake.api.suspend_d")
            clazz = getattr(suspend_d_module, "SuspendD")
            return clazz()

        if name == 'bak_daily':
            bak_daily_module = import_module("tutake.api.bak_daily")
            clazz = getattr(bak_daily_module, "BakDaily")
            return clazz()

        if name == 'stock_basic':
            stock_basic_module = import_module("tutake.api.stock_basic")
            clazz = getattr(stock_basic_module, "StockBasic")
            return clazz()

        if name == 'trade_cal':
            trade_cal_module = import_module("tutake.api.trade_cal")
            clazz = getattr(trade_cal_module, "TradeCal")
            return clazz()

        if name == 'namechange':
            namechange_module = import_module("tutake.api.namechange")
            clazz = getattr(namechange_module, "Namechange")
            return clazz()

        if name == 'hs_const':
            hs_const_module = import_module("tutake.api.hs_const")
            clazz = getattr(hs_const_module, "HsConst")
            return clazz()

        if name == 'stock_company':
            stock_company_module = import_module("tutake.api.stock_company")
            clazz = getattr(stock_company_module, "StockCompany")
            return clazz()

        if name == 'new_share':
            new_share_module = import_module("tutake.api.new_share")
            clazz = getattr(new_share_module, "NewShare")
            return clazz()

        if name == 'stk_managers':
            stk_managers_module = import_module("tutake.api.stk_managers")
            clazz = getattr(stk_managers_module, "StkManagers")
            return clazz()

        if name == 'stk_rewards':
            stk_rewards_module = import_module("tutake.api.stk_rewards")
            clazz = getattr(stk_rewards_module, "StkRewards")
            return clazz()

        if name == 'bak_basic':
            bak_basic_module = import_module("tutake.api.bak_basic")
            clazz = getattr(bak_basic_module, "BakBasic")
            return clazz()

        if name == 'index_basic':
            index_basic_module = import_module("tutake.api.index_basic")
            clazz = getattr(index_basic_module, "IndexBasic")
            return clazz()


if __name__ == '__main__':
    dao1 = DAO()
    print(dao1.stock_basic.count())
