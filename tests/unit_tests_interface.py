import os
import sys
import re
import traceback


class UnitTests(object):
    def __init__(self):
        pass

    def _run_correctness_tests(self):
        tests = []
        for item in dir(self):
            if re.match(r'^[^_].*$', item) and item != 'run':
                tests.append(item)

        all_tests_count = len(tests)
        passed_tests_count = 0
        failed_tests_count = 0
        for func_name in tests:
            func = getattr(self, func_name)
            title_parts = str(func_name).split('__')
            title = title_parts[0] + ' - ' + title_parts[1].replace('_', ' ')
            try:
                func()
                print '{0}: OK'.format(title)
                passed_tests_count += 1
            except AssertionError:
                tb = sys.exc_info()[2]
                tb_info = traceback.extract_tb(tb)
                line = tb_info[-1][1]
                print '{0}: FAILED at line {1}'.format(title, line)
                failed_tests_count += 1

        pass_rate = 100 * float(passed_tests_count) / all_tests_count
        print
        print 'All tests:', all_tests_count
        print 'Passed tests:', passed_tests_count
        print 'Failed tests:', failed_tests_count
        print 'PASS RATE: {0:.2f}%'.format(pass_rate)

    def _run_performance_tests(self):
        tests = []
        for item in dir(self):
            if re.match(r'^[^_].*$', item) and item != 'run':
                tests.append(item)

        for func_name in tests:
            func = getattr(self, func_name)
            title_parts = str(func_name).split('__')
            title = title_parts[0] + ' - ' + title_parts[1].replace('_', ' ')

            time = func()
            print '{0}: OK, time: {1:.2f}s'.format(title, time)
