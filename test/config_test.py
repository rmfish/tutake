import unittest

from tutake.utils.config import DotConfig


class Test(unittest.TestCase):
    def test_set_one_dot(self):
        config = DotConfig()
        config.set("a", 'a')
        self.assertEqual('a', config.get('a'))
        self.assertEqual('a', config.a)
        self.assertEqual('a', config['a'])

        v = {"b": {"c:": 'c'}}
        config.set("b", v)
        self.assertEqual(v, config.get('b'))
        self.assertEqual(v, config.b)
        self.assertEqual(v, config['b'])

    def test_set_two_dot(self):
        config = DotConfig()
        key = 'a.b'
        v = 'a'
        config.set(key, v)
        self.assertEqual(v, config.get(key))
        self.assertEqual(v, config.a.b)
        self.assertEqual(v, config[key])

        key = 'a.b'
        v = {"b": {"c:": 'c'}}
        config.set(key, v)
        self.assertEqual(v, config.get(key))
        self.assertEqual(v, config.a.b)
        self.assertEqual(v, config[key])

    def test_set_multi_dot(self):
        config = DotConfig()
        key = 'a.b.c.d'
        v = 'a'
        config.set(key, v)
        self.assertEqual(v, config.get(key))
        self.assertEqual(v, config.a.b.c.d)
        self.assertEqual(v, config[key])

        key = 'a.b.c.d'
        v = {"b": {"c:": 'c'}}
        config.set(key, v)
        self.assertEqual(v, config.get(key))
        self.assertEqual(v, config.a.b.c.d)
        self.assertEqual(v, config[key])

        key = 'a.b.c.e'
        self.assertEqual(None, config.get(key))
        self.assertEqual(None, config.a.b.c.e)
        self.assertEqual(None, config[key])

    def test_update(self):
        config = DotConfig()
        key = 'a.b.c.d'
        v = 'a'
        config.set(key, v)
        self.assertEqual(v, config.get(key))
        self.assertEqual(v, config.a.b.c.d)
        self.assertEqual(v, config[key])

        v = 'adsfasdf'
        config.set(key, v)
        self.assertEqual(v, config.get(key))
        self.assertEqual(v, config.a.b.c.d)
        self.assertEqual(v, config[key])
