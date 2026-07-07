import unittest
from src import email_utils

class TestEmailUtils(unittest.TestCase):
    def test_send_email_empty(self):
        # Should not raise, just print message
        try:
            email_utils.send_email("")
        except Exception as e:
            self.fail(f"send_email raised Exception unexpectedly: {e}")

if __name__ == '__main__':
    unittest.main()
