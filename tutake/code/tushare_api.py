"""
Tushare的Api列表，可用于生成自动化的接口
"""
import json
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from os import walk

import requests
from sqlalchemy import create_engine, MetaData, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tutake.utils.config import tutake_config
from tutake.utils.utils import project_root
from tutake.utils.singleton import Singleton

engine = create_engine("%s/%s" % (tutake_config.get_meta_sqlite_driver_url(), 'tushare_meta.db'))
session_factory = sessionmaker()
session_factory.configure(bind=engine)

Base = declarative_base()
metadata = MetaData(engine)


class TushareApiInterface(metaclass=ABCMeta):
    @abstractmethod
    def get_api_children(self, parent_id): pass

    @abstractmethod
    def get_ready_api(self, ): pass

    @abstractmethod
    def get_all_leaf_api(self, ): pass

    @abstractmethod
    def get_api(self, api_id): pass

    @abstractmethod
    def get_api_by_name(self, name): pass


class TushareApi(Base):
    __tablename__ = "tushare_api"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    desc = Column(String)
    parent_id = Column(Integer)
    name = Column(String)
    inputs = Column(String)
    outputs = Column(String)
    validations = Column(String)
    is_ready = Column(Integer)

    def __init__(self, api_id, title, desc, parent_id):
        self.id = api_id
        self.title = title
        self.desc = desc
        self.parent_id = parent_id


TushareApi.__table__.create(bind=engine, checkfirst=True)


class TushareDBApi(TushareApiInterface):

    def add_new_api(self, session, api_id, title, desc, parent_id):
        """Adds a new api to the system"""
        # Get the author's first and last names
        # Check if book exists
        api = session.query(TushareApi).get(api_id)
        if api is not None:
            return
        api = TushareApi(api_id, title, desc, parent_id)
        session.add(api)

        # Commit to the database
        session.commit()

    def update_api_detail(self, session, api_id, api_json):
        api = session.query(TushareApi).get(api_id)
        if api is None:
            return
        api.name = api_json['name']
        api.inputs = json.dumps(api_json['inputs'])
        api.outputs = json.dumps(api_json['outputs'])
        api.validations = json.dumps(api_json['validations'])
        session.add(api)
        session.commit()

    def get_api_children(self, parent_id):
        apis = session_factory().query(TushareApi).filter_by(parent_id=parent_id).all()
        if apis:
            return [self._assemble_api(i) for i in apis]

    def get_ready_api(self, ):
        apis = session_factory().query(TushareApi).filter_by(is_ready=1).all()
        if apis:
            return [self._assemble_api(i) for i in apis]

    def get_all_leaf_api(self, ):
        """
        获得所有子接口
        :return:
        """
        apis = session_factory().query(TushareApi).all()
        parent_ids = [_api.parent_id for _api in apis if _api.parent_id]
        leaf_apis = [api for api in apis if api.id not in parent_ids]
        if leaf_apis:
            return [self._assemble_api(i) for i in leaf_apis]

    def get_api(self, api_id):
        api = session_factory().query(TushareApi).get(api_id)
        return self._assemble_api(api)

    def get_api_by_name(self, name):
        return session_factory().query(TushareApi).filter_by(name=name).one()

    def _assemble_api(self, api):
        if api is None:
            return None
        obj = api.__dict__
        if obj.get('inputs'):
            obj["inputs"] = json.loads(obj["inputs"])
        if obj.get('outputs'):
            obj["outputs"] = json.loads(obj["outputs"])
        if obj.get('validations'):
            obj["validations"] = json.loads(obj["validations"])
        if obj.get('_sa_instance_state'):
            del obj['_sa_instance_state']
        return obj

    def get_api_path(self, api_id):
        api = session_factory().query(TushareApi).get(api_id)
        path = [(api.id, api.title)]
        while api.parent_id is not None:
            api = session_factory().query(TushareApi).get(api.parent_id)
            path.insert(0, (api.id, api.title))
        return path

    def dump(self):
        cookie = tutake_config.get_config("tushare.meta.cookie")

        def save_api(apis, parent_id=None):
            for i in range(len(apis)):
                api = apis[i]
                api_id = api['id']
                self.add_new_api(session_factory(), api_id, api['title'], api["desc"], parent_id)
                api_detail = self.api_http(api_id, cookie)
                if len(api["children"]) == 0:
                    print("Update api detail. id:{0} name:{1}".format(api_id, api['title']))
                    if api_detail is not None:
                        self.update_api_detail(session_factory(), api_id, api_detail)
                save_api(api["children"], api_id)

        metabase = self.api_tree_http(cookie)
        save_api(metabase)

    def api_http(self, api_id, cookie):
        return self.http_get("https://tushare.pro/wctapi/documents/{0}/api_info".format(api_id), cookie)

    def api_tree_http(self, cookie):
        """
        从http接口中获取api的元数据
        """
        return self.http_get("https://tushare.pro/wctapi/documents/tree", cookie)

    def http_get(self, url, cookie):
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Cookie': cookie
        }
        r = requests.get(url, timeout=10, headers=headers)
        return r.json()['data']


@Singleton
class TushareJsonApi(TushareApiInterface):

    def __init__(self):
        self._load_config()

    def _load_config(self):
        config_dir = "{}/tutake/api/tushare/config".format(project_root())
        files = []
        for (dirpath, dirnames, filenames) in walk(config_dir):
            files.extend(filenames)
            break
        apis = {}
        for f in files:
            file_path = "{}/{}".format(config_dir, f)
            apis[f[:-5]] = json.load(open(file_path))
        self.apis = apis

    def _write_config(self, config):
        config_path = "{}/tutake/api/tushare/config/{}.json".format(project_root(), config['name'])
        with open(config_path, "w") as file:
            file.write(json.dumps(OrderedDict(config), indent=4, ensure_ascii=False, sort_keys=True))

    def get_api_children(self, parent_id):
        return [api for api in self.apis.values() if api['parent_id'] == parent_id]

    def get_ready_api(self):
        return [api for api in self.apis.values() if api.get('is_ready') == 1]

    def get_all_leaf_api(self):
        return [api for api in self.apis.values() if api.get('name')]

    def get_api(self, api_id):
        api = [api for api in self.apis.values() if api.get('id') == api_id]
        if len(api) > 0:
            return api[0]
        return None

    def get_api_by_name(self, name):
        api = [api for api in self.apis.values() if api.get('name') == name]
        if len(api) > 0:
            return api[0]
        return None

    def update_api(self, config: dict):
        if config and config.get("id"):
            api = self.get_api(config.get("id"))
            config = {key: value for key, value in config.items() if value is not None and str(value) != ''}
            if api:
                api = {**api, **config}
            else:
                api = config
            if api.get('name'):
                self.apis[api['name']] = api
                self._write_config(api)
            else:
                print("Null {}".format(api))

    def get_all(self):
        return self.apis.values()


if __name__ == '__main__':
    json_config = TushareJsonApi()
    db_config = TushareDBApi()
    for i in json_config.get_all_leaf_api():
        if i.get('default_limit'):
            i['default_limit'] = str(i.get('default_limit'))
        i['default_cron'] = "10 0 * * *"
        json_config.update_api(i)
