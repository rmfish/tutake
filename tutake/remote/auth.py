import logging
import os
import sqlite3
import sys
from typing import Dict, Set

import zmq
import zmq.auth
from tutake.remote.exception import SQLiteRxAuthConfigError


LOG = logging.getLogger(__name__)

__all__ = ['Authorizer', 'KeyGenerator', 'KeyMonkey', 'DEFAULT_AUTH_CONFIG']

# Default Authorization Config
DEFAULT_AUTH_CONFIG = {
    sqlite3.SQLITE_OK: {
        sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_TABLE,
        sqlite3.SQLITE_CREATE_TEMP_INDEX,
        sqlite3.SQLITE_CREATE_TEMP_TABLE,
        sqlite3.SQLITE_CREATE_TEMP_TRIGGER,
        sqlite3.SQLITE_CREATE_TEMP_VIEW,
        sqlite3.SQLITE_CREATE_TRIGGER,
        sqlite3.SQLITE_CREATE_VIEW,
        sqlite3.SQLITE_INSERT,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_TRANSACTION,
        sqlite3.SQLITE_UPDATE,
        sqlite3.SQLITE_ATTACH,
        sqlite3.SQLITE_DETACH,
        sqlite3.SQLITE_ALTER_TABLE,
        sqlite3.SQLITE_REINDEX,
        sqlite3.SQLITE_ANALYZE,
    },

    sqlite3.SQLITE_DENY: {
        sqlite3.SQLITE_DELETE,
        sqlite3.SQLITE_DROP_INDEX,
        sqlite3.SQLITE_DROP_TABLE,
        sqlite3.SQLITE_DROP_TEMP_INDEX,
        sqlite3.SQLITE_DROP_TEMP_TABLE,
        sqlite3.SQLITE_DROP_TEMP_TRIGGER,
        sqlite3.SQLITE_DROP_TEMP_VIEW,
        sqlite3.SQLITE_DROP_TRIGGER,
        sqlite3.SQLITE_DROP_VIEW,
    },

    sqlite3.SQLITE_IGNORE: {
        sqlite3.SQLITE_PRAGMA
    }

}


class Authorizer:

    def __init__(self, config: Dict[int, Set[int]] = None):
        """Represents the authorization config which can be passed to the :class: ``sqlite_rx.server.SQLiteServer``
        class during server startup. This class represents a callable passed to the sqlite3's
        ``set_authorizer()`` method.

        Args:
            config: A dictionary which maps ``permissions`` to sqlite3 ``actions``. Valid
            permissions are ``sqlite3.SQLITE_OK``, ``sqlite3.SQLITE_DENY`` and ``sqlite3.SQLITE_IGNORE``

        Raises:
            sqlite_rx.exception.SQLiteRxAuthConfigError: if ``config`` contains invalid permissions other than
            ``sqlite3.SQLITE_OK``, ``sqlite3.SQLITE_DENY`` and ``sqlite3.SQLITE_IGNORE``

        Example:
            >>> from tutake.remote.auth import Authorizer
            >>> auth_config = {
            >>>                  sqlite3.SQLITE_DENY: {sqlite3.SQLITE_CREATE_INDEX, sqlite3.SQLITE_CREATE_TABLE}
            >>>               }
            >>> authorizer = Authorizer(config=auth_config)

        """
        self.config = config if config else DEFAULT_AUTH_CONFIG
        self.valid_return_values = {
            sqlite3.SQLITE_IGNORE,
            sqlite3.SQLITE_OK,
            sqlite3.SQLITE_DENY}
        if any(k not in self.valid_return_values for k in self.config.keys()):
            raise SQLiteRxAuthConfigError(
                "Allowed return values are: "
                "sqlite3.SQLITE_OK(0), sqlite3.SQLITE_DENY(1), sqlite3.SQLITE_IGNORE(2)")

    def __call__(self, action: int, *args, **kwargs) -> int:
        """Returns the permission for the passed ``action``

        Args:
            action: The integer representing the action for which permission is to be fetched.

        Returns:
            The permission ``sqlite3.SQLITE_OK``, ``sqlite3.SQLITE_IGNORE`` or ``sqlite3.SQLITE_DENY``
            as defined in the configuration passed to the ``__init__()`` method.
            Default is ``sqlite3.SQLITE_OK``

        """
        for return_val, actions in self.config.items():
            if action in actions:
                return return_val
        return sqlite3.SQLITE_OK


class KeyGenerator:

    def __init__(self,
                 key_id: str = "id_curve",
                 destination_dir: str = None):
        """Generates curve public and private keys required for encryption.
        This class should not be used by users to generate keys.
        Use the script ``curve-keygen``

        Args:
            key_id: This is the name of the curve key. 2 keys will be generated of the form
            ``<key_id>.key"`` and ``<key_id>.key_secret``

            destination_dir: Directory location where to generate the public and private keys.
            Default is ``~/.curve/`` just like ``~/.ssh``

        Examples:
            >>> from tutake.remote.auth import KeyGenerator
            >>> key_gen = KeyGenerator(key_id="id_server_curve")
            >>> key_gen.generate()

        """
        self.my_id = key_id
        self.curvedir = destination_dir if destination_dir else os.path.join(
            os.path.expanduser("~"), ".curve")
        self.public_key = os.path.join(
            self.curvedir, "{}.key".format(self.my_id))
        self.private_key = os.path.join(
            self.curvedir,
            "{}.key_secret".format(
                self.my_id))
        self.authorized_clients_dir = os.path.join(
            self.curvedir, "authorized_clients")

    def generate(self):
        """

        1. Makes the directory ``destination_dir`` and ``destination_dir/authorized_clients`` if not present.
        2. Generates private and public curve keys.

        """
        bogus = False
        for key in [self.public_key, self.private_key]:
            if os.path.exists(key):
                LOG.info("%s already exists. Aborting.", key)
                bogus = True
                break
        if bogus:
            sys.exit(1)

        if not os.path.exists(self.curvedir):
            os.mkdir(self.curvedir)

        if not os.path.exists(self.authorized_clients_dir):
            os.mkdir(self.authorized_clients_dir)

        os.chmod(self.curvedir, 0o700)
        os.chmod(self.authorized_clients_dir, 0o700)

        server_public_file, server_secret_file = zmq.auth.create_certificates(
            self.curvedir, self.my_id)
        LOG.info(server_public_file)
        LOG.info(server_secret_file)
        os.chmod(self.public_key, 0o600)
        os.chmod(self.private_key, 0o600)
        LOG.info("Created Public key %s", self.public_key)
        LOG.info("Created Private key %s", self.private_key)


class KeyMonkey:

    def __init__(self,
                 key_id: str = "id_curve",
                 destination_dir: str = None):
        """Setup secure client or server using the CurveZMQ

        This class expects the following keys depending on whether you want to setup a secure server
        or secure client.

        ~/.curve/id_server_curve.key
        ~/.curve/id_server_curve.key-secret


        Args:
             key_id: This is the name of the curve key. 2 keys are expected which are of the form
            ``<key_id>.key"`` and ``<key_id>.key_secret``

            destination_dir: Directory location where to read the public and private keys from.
            Default directory location is ``~/.curve/`` just like ``~/.ssh``

        """

        self.my_id = key_id
        self.curvedir = destination_dir if destination_dir else os.path.join(os.path.expanduser("~"), ".curve")
        self.public_key = os.path.join(self.curvedir, "{}.key".format(self.my_id))
        self.private_key = os.path.join(self.curvedir, "{}.key_secret".format(self.my_id))
        self.authorized_clients_dir = os.path.join(self.curvedir, "authorized_clients")

    def setup_secure_server(self,
                            server,
                            bind_address: str):
        """
        Use this method to setup a secure server.

        Args:
            server: ZMQ Socket instance
            bind_address: Address on which the server will listen for client connections

        Raises:
            IOError: When keys are not found.

        """
        try:
            server.curve_publickey, server.curve_secretkey = zmq.auth.load_certificate(self.private_key)
            server.curve_server = True
            LOG.info("Secure setup completed using on %s using curve key %s", bind_address, self.my_id)
            return server
        except IOError:
            LOG.exception("Couldn't load the private key: %s", self.private_key)
            raise
        except Exception:
            LOG.exception("Exception while setting up CURVECP")
            raise

    def setup_secure_client(self,
                            client,
                            connect_address: str,
                            servername: str):
        """
        Use this method to setup a secure client. Clients also need the
        servername to look for server's public key

        Args:
            client: A ZMQ Socket instance

            connect_address: The address of the server where the clients will send requests

            servername: To look for the server public key. If the server public key is ``id_server_curve.key``
            then servername should be ``id_server_curve``

        Raises:
            IOError: When keys are not found

        """
        try:
            client.curve_publickey, client.curve_secretkey = zmq.auth.load_certificate(self.private_key)
        except IOError:
            LOG.exception("Couldn't load the client private key: %s", self.private_key)
            raise
        else:
            # Clients need server's public key for encryption
            try:
                client.curve_serverkey, _ = zmq.auth.load_certificate(os.path.join(self.curvedir, f"{servername}.key"))
            except IOError:
                LOG.exception(
                    "Couldn't load the server public key %s ", os.path.join(self.curvedir, f"{servername}.key"))
                raise
            else:
                LOG.info("Client connecting to %s (key %s) using curve key '%s'.",
                         connect_address, servername, self.my_id)
                return client
