import os
import sys
import time
from py2neo import neo4j
from unit_tests_interface import UnitTests
sys.path.append(os.path.join(os.path.dirname(__file__), '../lionfish/python_lionfish/client'))
from client import Client


class LionfishPerformanceUnitTests(UnitTests):
    def __init__(self):
        super(LionfishPerformanceUnitTests, self).__init__()
        self.run = self._run_performance_tests
        self._client = Client()
        self._client.connect()
        self._batch = self._client.get_batch()

    def create_and_delete_node__regular500(self):
        for i in range(0, 500):
            self._batch.append(self._client.create_node, 'NeoUser', p='ok')
        start_time = time.time()
        uuids = self._batch.submit()

        for item in uuids:
            self._batch.append(self._client.delete_node, item)
        self._batch.submit()
        end_time = time.time()

        return end_time - start_time

    def create_and_delete_node__regular8000(self):
        for i in range(0, 8000):
            self._batch.append(self._client.create_node, 'Content', p='ok')
        start_time = time.time()
        uuids = self._batch.submit()

        for item in uuids:
            self._batch.append(self._client.delete_node, item)
        self._batch.submit()
        end_time = time.time()

        return end_time - start_time


if __name__ == "__main__":
    unit_tests = LionfishPerformanceUnitTests()
    unit_tests.run()
