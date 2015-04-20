#-*- coding:utf-8 -*-

import os
import sys
import unittest
import random
import time
import threading
import logging

import realpath
import log

test_log = log.getLogger(__file__)

base_path = os.path.abspath(__file__)
base_name = os.path.basename(base_path)
#test_log_name = '.'.join(base_path.split('/')[1:-1]+[base_name.replace('.py', '')])


class GetLoggerTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_logger(self):
        # module file log
        #self.assertEqual(test_log.name, test_log_name)

        # root logger
        self.assertEqual(log.getLogger(), logging.root)
        self.assertEqual(len(log.getLogger(log_path='root.log').handlers), 2)
        self.assertEqual(len(log.getLogger(log_path='root2.log').handlers), 2)
        self.assertEqual(len(log.getLogger(log_level=logging.WARNING, log_path='root3.log').handlers), 3)

        # normal logger no handlers
        logger_one = log.getLogger('logger.one')
        self.assertEqual(logger_one.name, 'logger.one')
        self.assertEqual(len(logger_one.handlers), 0)

        # file handler one level only have only handler
        logger_two = log.getLogger('logger.two', logging.DEBUG, 'logger_test.log')
        self.assertEqual(len(logger_two.handlers), 1)
        logger_two_2 = log.getLogger('logger.two', logging.DEBUG, 'logger_test2.log')
        self.assertEqual(len(logger_two.handlers), 1)
        logger_two_2 = log.getLogger('logger.two', logging.ERROR, 'logger_test3.log')
        self.assertEqual(len(logger_two.handlers), 2)


if __name__ == '__main__':
    unittest.main()
