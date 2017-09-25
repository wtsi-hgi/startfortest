from enum import Enum, unique
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock

import os

from Cryptodome.PublicKey import RSA
from typing import Callable, Dict


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
        return self.lazy_get_value(_KeyType.PRIVATE, lambda: self._key.exportKey().decode(_UTF8_ENCODING))

    @property
    def public_key(self) -> str:
        return self.lazy_get_value(_KeyType.PUBLIC, lambda: self._key.publickey().exportKey("OpenSSH").decode(_UTF8_ENCODING))

    @property
    def private_key_file(self) -> str:
        return self._lazy_get_file(_KeyType.PRIVATE, lambda: self.private_key)

    @property
    def public_key_file(self) -> str:
        return self._lazy_get_file(_KeyType.PUBLIC, lambda: self.public_key)

    def __init__(self, key_length: int=2048):
        """
        Constructor.
        :param key_length: length of the RSA key to generate.
        """
        self._key = RSA.generate(key_length)
        self._values: Dict[_KeyType, str] = {}
        self._file_locations: Dict[_KeyType: str] = {}
        self._locks = {
            _KeyType.PRIVATE: Lock(),
            _KeyType.PUBLIC: Lock()
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
                if key_type in self._file_locations:
                    try:
                        os.remove(self._file_locations[key_type])
                    except OSError:
                        pass

    def lazy_get_value(self, key_type: _KeyType, data_source: Callable[[], str]):
        """
        Lazily get the value associated to the given key type, generating it from the given data source and saving it to
        the value cache if it has not been set.
        :param key_type: the type of the key
        :param data_source: the source to generate the value from if not generated
        :return: the value associated to the given key
        """
        if key_type not in self._values:
            self._values[key_type] = data_source()
        return self._values[key_type]

    def _lazy_get_file(self, key_type: _KeyType, data_source: Callable[[], str]) -> str:
        """
        Lazily gets the file associated to the given key type, generating it from the given data source and saving it to
        the file cache if it has not been set.
        :param key_type: the type of the key
        :param data_source: the source to generate the file from if not generated
        :return: the file associated to the given key
        """
        if key_type not in self._file_locations:
            with self._locks[key_type]:
                if key_type not in self._file_locations:
                    temp_file = NamedTemporaryFile().name
                    Path(temp_file).touch()
                    os.chmod(temp_file, 0o600)
                    with open(temp_file, "w") as file:
                        file.write(data_source())
                    self._file_locations[key_type] = temp_file
        return self._file_locations[key_type]
