
class SQLiteRxError(Exception):
    pass


class SQLiteRxAuthConfigError(SQLiteRxError):
    pass


class SQLiteRxZAPSetupError(SQLiteRxError):
    pass


class SQLiteRxTransportError(SQLiteRxError):
    pass


class SQLiteRxSerializationError(SQLiteRxError):
    pass


class SQLiteRxCompressionError(SQLiteRxError):
    pass


class SQLiteRxConnectionError(SQLiteRxError):
    pass

class SQLiteRxBackUpError(SQLiteRxError):
    pass