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

        if name == 'ggt_top10':
            ggt_top10_module = import_module("tutake.api.tushare.ggt_top10")
            clazz = getattr(ggt_top10_module, "GgtTop10")
            return clazz()
