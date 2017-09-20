import unittest

import os

from useintest.predefined.gitlab import SshKey


class TestSshKey(unittest.TestCase):
    """
    Tests for `SshKey`.
    """
    def test_enter_exit_when_no_file_used(self):
        with SshKey():
            pass

    def test_private_key_file(self):
        with SshKey() as ssh_key:
            location = ssh_key.private_key_file
            with open(location, "r") as file:
                self.assertEqual(ssh_key.private_key, file.read())
        self.assertFalse(os.path.exists(location))

    def test_public_key_file(self):
        with SshKey() as ssh_key:
            location = ssh_key.public_key_file
            with open(location, "r") as file:
                self.assertEqual(ssh_key.public_key, file.read())
        self.assertFalse(os.path.exists(location))

    def test_all_key_files(self):
        with SshKey() as ssh_key:
            private_key_file, public_key_file = ssh_key.private_key_file, ssh_key.public_key_file
        self.assertFalse(os.path.exists(private_key_file))
        self.assertFalse(os.path.exists(public_key_file))


if __name__ == "__main__":
    unittest.main()
