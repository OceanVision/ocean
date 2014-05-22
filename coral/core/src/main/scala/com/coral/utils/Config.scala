package com.coral.utils

object Config {
  val webserviceConnectorPort = 7778
  val masterSystemPort = 7779
  val sessionWorkerSystemPort = 7780
  val cacheWorkerSystemPort = 7781
  val databaseWorkerSystemPort = 7782
  val cachePort = 7783

  var numberOfRequestHandlers = 10
  var numberOfCacheWorkers = 10
  var numberOfDatabaseWorkers = 10
}
