from __future__ import print_function
import unittest

from mock import Mock

import pokemongo_bot
from pokemongo_bot import EventManager
from pokemongo_bot import Logger


class LoggerTest(unittest.TestCase):
    @staticmethod
    def test_log_by_call():
        import sys
        from io import StringIO
        out = StringIO()
        sys.stdout = out

        logger = Logger().getLogger('test')

        logger.info("log row", color="yellow")
        output = out.getvalue().strip()
        assert "[test] log row" in output
