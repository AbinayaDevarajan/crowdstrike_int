
import redis
from redis import RedisError
from contextlib import asynccontextmanager
from contextlib import contextmanager

class DummyConnection(object):
    description_format = "DummyConnection<>"

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.pid = os.getpid()

    def connect(self):
        pass

    def can_read(self):
        return False


class RedisUtils:
    def __init__(self, is_blocking_pool=False):
        self.is_blocking_pool = is_blocking_pool
        self.pool = None

    def get_pool(self,
                 connection_kwargs=None,
                 max_connections=None,
                 connection_class=redis.Connection):
        """
            Get the redis configuration pool
        """

        connection_kwargs = connection_kwargs or {}
        pool = redis.ConnectionPool(
            connection_class=connection_class,
            max_connections=max_connections,
            **connection_kwargs)
        return pool

    def get_blocking_pool(self,
                          connection_kwargs=None,
                          max_connections=10,
                          timeout=20):
        connection_kwargs = connection_kwargs or {}
        pool = redis.BlockingConnectionPool(
            connection_class=DummyConnection,
            max_connections=max_connections,
            timeout=timeout,
            **connection_kwargs)
        return pool

    @contextmanager
    def connect_to_redis(self, *args, **kwds):

        # Code to acquire connection, e.g.:
        resource = self.connect(*args, **kwds)
        try:
            yield resource
        finally:
            # Code to release connection, e.g.:
            self.pool.release(self.connection)

    def strict_connect(self, **connection_kwargs):

        self.connection = redis.StrictRedis(host=connection_kwargs.get("host"), port=connection_kwargs.get("port"), db=connection_kwargs.get("db"),
                                            decode_responses=True)
        return self.connection

    def connect(self, **connection_kwargs):
        """
            Get the connect to the redis server , blocking , non blocking pool
        """
        try:
            if self.is_blocking_pool:

                self.pool = self.get_blocking_pool(
                    connection_kwargs=connection_kwargs,
                    connection_class=redis.Connection,
                    max_connections=10,
                    timeout=60)
            else:
                self.pool = self.get_pool(
                    connection_kwargs=connection_kwargs,
                    connection_class=redis.Connection)

            expected = ('ConnectionPool<Connection<'
                        'host={},port={},db={},client_name={}>>'.format(
                            connection_kwargs.get('host'),
                            connection_kwargs.get('port'),
                            connection_kwargs.get('db'),
                            connection_kwargs.get('client_name'),
                        ))
            assert repr(self.pool) == expected
            self.connection = redis.StrictRedis(
                connection_pool=self.pool, decode_responses=True)
            self.connection.ping()
            LOGGER.info("connection established to the redis {}".format(
                self.connection))
        except Exception as e:
            LOGGER.error("Exception occured when connecting to redis" + str(e))
            raise redis.exceptions.ConnectionError(
                "Exception occurred during the connection to redis server")

    def get_database_config(self):
        """
            Get the redis configuration pool
        """

        try:
            data = self.connection.config_get()
            assert 'maxmemory' in data
            assert data['maxmemory'].isdigit()
            return (DictionaryObject(data))
        except Exception as e:
            raise RedisError(
                "Exception occurred while getting the configuration for redis")

    def insert_dict_to_database(self, dictionary):
        """
           insert information to redis
        """
        try:
            self.connection.mset(dictionary)
        except AttributeError as e:
            LOGGER.error(
                "Exception occurred, please, send dictionary input" + str(e))
            raise RedisError(
                "Please, send only the dictionary for insertion in to redis")

    def get_keys(self):
        """
           get the keys 
        """

        try:
            return self.connection.keys()
        except Exception as e:
            LOGGER.error(
                "Exception occurred, please, send dictionary input" + str(e))
            raise RedisError(
                "Please, send only the dictionary for insertion in to redis")
