from enum import Enum, unique
from tempfile import NamedTemporaryFile
from threading import Lock

import os
from typing import Callable, Optional, Dict

from Crypto.PublicKey import RSA

_UTF8_ENCODING = "utf-8"


@unique
class _KeyType(Enum):
    """"
    Types of keys.
    """
    PRIVATE = "private"
    PUBLIC = "public"


class SshKey:
    """
    Wrapper to help use an SSH key.
    """
    @property
    def private_key(self) -> str:
        return self._key.exportKey().decode(_UTF8_ENCODING)

    @property
    def public_key(self) -> str:
        return self._key.publickey().exportKey().decode(_UTF8_ENCODING)

    @property
    def private_key_file(self) -> str:
        return self._lazy_get(_KeyType.PRIVATE, lambda: self.private_key)

    @property
    def public_key_file(self) -> str:
        return self._lazy_get(_KeyType.PUBLIC, lambda: self.public_key)

    def __init__(self, key_length: int=2048):
        """
        Constructor.
        :param key_length: length of the RSA key to generate.
        """
        self._key = RSA.generate(key_length)
        self._locks = {
            _KeyType.PRIVATE: Lock(),
            _KeyType.PUBLIC: Lock()
        }
        self._value_cache: Dict[Optional[str]] = {
            _KeyType.PRIVATE: None,
            _KeyType.PUBLIC: None
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tear_down()

    def tear_down(self):
        """
        Removes temp files managed by this instance.
        """
        for key_type, lock in self._locks.items():
            with lock:
                key_file = self._value_cache[key_type]
                if key_file is not None:
                    try:
                        os.remove(key_file)
                    except OSError:
                        pass

    def _lazy_get(self, key_type: _KeyType, data_source: Callable[[], str]) -> str:
        """
        Lazily gets the value associated to the given key type, generating it from the given data source and saving it
        to the value cache if it has not been set.
        :param key_type: the type of the key
        :param data_source: the source to generate the value if not generated
        :return: the value associated to the given key
        """
        if self._value_cache[key_type] is None:
            with self._locks[key_type]:
                if self._value_cache[key_type] is None:
                    temp_file = NamedTemporaryFile().name
                    with open(temp_file, "w") as file:
                        file.write(data_source())
                    self._value_cache[key_type] = temp_file
        return self._value_cache[key_type]
