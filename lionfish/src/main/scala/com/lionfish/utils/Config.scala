package com.lionfish.utils

object Config {
  val masterSystemPort = 7775
  val cacheWorkerSystemPort = 7774
  val databaseWorkerSystemPort = 7773
  var cachePort = 7772

  var serverAddress = "ocean-lionfish.no-ip.biz"
  var serverPort = 21
  var neo4jPath = "/usr/lib/neo4j"
  var neo4jConsolePort = 7474
  var useCache = false

  var numberOfRequestHandlers = 10
  var numberOfCacheWorkers = 10
  var numberOfDatabaseWorkers = 10
}
