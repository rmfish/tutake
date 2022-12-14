from abc import ABCMeta


class Symbol(metaclass=ABCMeta):
    """
    股票代码,不同的市场有不同的代码处理，通过这个实现了统一处理，标准的形式为 CODE.EXCHANGE 例如 000002.SZ
    """

    def __init__(self, _code: str, _exchange: str):
        self.code = _code
        self.exchange = _exchange

    def trade_code(self):
        if self.exchange:
            return f"{self.code}.{self.exchange.upper()}"
        else:
            return self.code

    def __str__(self):
        return self.trade_code()

    def __getattr__(self, item):
        if item == "tushare":
            return TushareSymbol.convert(self)
        elif item == "xq" or item == "xueqiu":
            return XueQiuSymbol.convert(self)


class SymbolConverter(metaclass=ABCMeta):
    """
    代码转化器，将代码类型转成其他的类型，比如雪球代码转成tushare类型
    """

    @classmethod
    def convert(cls, symbol: Symbol) -> str:
        pass


class TushareSymbol(Symbol, SymbolConverter):

    def __init__(self, _code: str):
        if '.' in _code:
            tokens = _code.split(".")
            super().__init__(tokens[0], tokens[1])
        else:
            super().__init__(_code, "")

    @classmethod
    def convert(cls, symbol: Symbol) -> str:
        return symbol.trade_code()


class XueQiuSymbol(Symbol, SymbolConverter):

    def __init__(self, _code):
        if _code.startswith("SH") or _code.startswith("SZ") or _code.startswith("BJ"):
            super().__init__(_code[2:], _code[0:2])
        elif _code.isnumeric():
            super().__init__(_code, "HK")
        else:
            super().__init__(_code, "")

    @classmethod
    def convert(cls, symbol: Symbol) -> str:
        return f"{symbol.exchange}{symbol.code}"


if __name__ == '__main__':
    code = TushareSymbol("000002.SZ")
    print(code.tushare)

    print(XueQiuSymbol("SZ000002").trade_code())
    print(XueQiuSymbol("WES0").trade_code())
    print(XueQiuSymbol("00700").trade_code())
    print(XueQiuSymbol("BABA").trade_code())
