import os
import sys
import time
from py2neo import neo4j
from unit_tests_interface import UnitTests
sys.path.append(os.path.join(os.path.dirname(__file__), '../graph_workers'))
from odm_client import ODMClient


class LionfishPerformanceUnitTests(UnitTests):
    def __init__(self):
        super(LionfishPerformanceUnitTests, self).__init__()
        self.run = self._run_performance_tests
        self._client = ODMClient()
        self._client.connect()
        self._batch = self._client.get_batch()
        graph_db = neo4j.GraphDatabaseService(
            'http://ocean-neo4j.no-ip.biz:7474/db/data/'
            # 'http://localhost:7474/db/data/'
        )
        self._v_read_batch = neo4j.ReadBatch(graph_db)
        self._v_write_batch = neo4j.WriteBatch(graph_db)

    def create_node__regular500(self):
        for i in range(0, 500):
            self._batch.append(self._client.create_node, 'Content', p='ok')
        start_time = time.time()
        uuids = self._batch.submit()
        end_time = time.time()

        assert(end_time - start_time < 2)
        return end_time - start_time

    def create_node__regular1000(self):
        for i in range(0, 1000):
            self._batch.append(self._client.create_node, 'Content', p='ok')
        start_time = time.time()
        uuids = self._batch.submit()
        end_time = time.time()

        assert(end_time - start_time < 2)
        return end_time - start_time


if __name__ == "__main__":
    unit_tests = LionfishPerformanceUnitTests()
    unit_tests.run()
