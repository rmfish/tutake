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



if __name__ == '__main__':
    dao1 = DAO()
    print(dao1.stock_basic.count())