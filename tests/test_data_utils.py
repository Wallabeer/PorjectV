import unittest
from src import data_utils

class TestDataUtils(unittest.TestCase):
    def test_get_session_with_retry(self):
        session = data_utils.get_session_with_retry()
        self.assertIsNotNone(session)
        self.assertTrue(hasattr(session, 'get'))

    def test_getData_invalid_url(self):
        session = data_utils.get_session_with_retry()
        result = data_utils.getData(session, 'http://invalid.url')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
