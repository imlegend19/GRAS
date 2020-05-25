import unittest
from unittest.mock import patch


class TestAlias(unittest.TestCase):
    @patch('gras.identity_merging.identity_merging.Alias.normalize_unicode_to_ascii')
    def test_normalise_string(self, func):
        result = func('महेन')
        self.assertEqual(result, 'mahen')


if __name__ == '__main__':
    unittest.main()
