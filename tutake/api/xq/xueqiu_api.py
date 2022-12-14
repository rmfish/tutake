from importlib import import_module


class XueQiuAPI(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config):
        self.instances = {}
        self.config = config
        pass

    def __getattr__(self, name):
        if not self.instances.get(name):
            self.instances[name] = self.instance_from_name(name, self.config)
        return self.instances.get(name)

    def all_apis(self):
        apis = ['index_valuation', 'hot_stock']
        return apis

    def instance_from_name(self, name, config):

        if name == 'index_valuation':
            index_valuation_module = import_module("tutake.api.xq.index_valuation")
            clazz = getattr(index_valuation_module, "IndexValuation")
            return clazz(config)
        if name == 'hot_stock':
            hot_stock_module = import_module("tutake.api.xq.hot_stock")
            clazz = getattr(hot_stock_module, "HotStock")
            return clazz(config)
        else:
            return None
