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

        if name == 'hsgt_top10':
            hsgt_top10_module = import_module("tutake.api.tushare.hsgt_top10")
            clazz = getattr(hsgt_top10_module, "HsgtTop10")
            return clazz()
