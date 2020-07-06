from abc import ABCMeta, abstractmethod
import logging
import time
import random
import socket

"""
36-37 section
"""


class LoggerMeta(type):
    def __init__(cls, what, bases=None, dict=None):
        print('IdGenerator.__init__ cls:', cls)
        dict['logger'] = logging.getLogger(cls.__name__) # 不起作用。。why 待调研
        super().__init__(what, bases, dict)


class IdGenerator(object, metaclass=LoggerMeta):
    """
    抽象类OR接口
    """
    @abstractmethod
    def generate(self) -> str:
        pass


class IdGenerationFailureException(Exception):
    pass


class UnknownHostException(Exception):
    pass


class IllegalArgumentException(Exception):
    pass


class RandomIdGenerator(IdGenerator):
    # test = 'test'
    logger = logging.getLogger('RandomIdGenerator')

    def generate(self) -> str:
        # substr_of_host_name = None
        try:
            substr_of_host_name = self.__get_last_field_of_host_name()
        except UnknownHostException as e:
            raise IdGenerationFailureException('...', e)

        current_time_millis = int(time.time()) * 1000
        random_str = self._generate_random_alphameric(8)
        id_str = "%s-%d-%s" % (substr_of_host_name, current_time_millis, random_str)
        return id_str

    def __get_last_field_of_host_name(self):
        host_name = socket.gethostname()
        if host_name is None or host_name == '':
            raise UnknownHostException('...')

        substr_of_host_name = self._last_substr_splitted_by_dot(host_name)
        # self.logger.fatal('failed to get the host name.', str(e))

        return substr_of_host_name

    def _last_substr_splitted_by_dot(self, host_name):
        if host_name is None or host_name == '':
            raise IllegalArgumentException('...')

        tokens = host_name.split('\\.')
        substr_of_host_name = tokens[len(tokens) - 1]
        return substr_of_host_name

    def _generate_random_alphameric(self, length):
        if length <= 0:
            raise IllegalArgumentException('...')

        random_chars = []
        count = 0
        max_ascii_ord = ord('z')
        while count < length:
            random_ascii = chr(random.randint(0, max_ascii_ord))
            is_digit = '0' <= random_ascii <= '9'
            is_uppercase = 'A' <= random_ascii <= 'Z'
            is_lowercase = 'a' <= random_ascii <= 'z'
            if is_digit or is_uppercase or is_lowercase:
                random_chars.append(random_ascii)
                count += 1
        return ''.join(random_chars)


if __name__ == '__main__':
    o = RandomIdGenerator()
    # o2 = RandomIdGenerator()
    print(o.generate())