package com.lionfish.workers

import java.net.InetSocketAddress
import akka.actor._
import net.spy.memcached.MemcachedClient
import com.lionfish.messages._
import com.lionfish.utils.Config
import com.lionfish.logging.Logging

class CacheWorker extends Actor {
  private val log = Logging
  private val masterSystemPort = Config.masterSystemPort
  private val databaseWorkerSystemPort = Config.databaseWorkerSystemPort
  private val cacheClient = new MemcachedClient(new InetSocketAddress("127.0.0.1", Config.cachePort))

  // Master worker
  private val masterPath =
    s"akka.tcp://masterSystem@localhost:$masterSystemPort/user/master"
  private val master = context.actorSelection(masterPath)

  // Database worker pool system
  private val databaseWorkerPath =
    s"akka.tcp://databaseWorkerSystem@localhost:$databaseWorkerSystemPort/user/databaseWorkerPool"
  private val databaseWorkerPool = context.actorSelection(databaseWorkerPath)

  // Decides whether fetch data from cache or database
  def processRequest(request: Request) = {
    val requestHash = request.hashCode().toString

    // If the user wants to use cache
    if (Config.useCache) {
      val cachedResult = cacheClient.get(requestHash)
      if (cachedResult != null) {
        // If the data exists in the cache
        val uuid = request.connectionUuid
        log.info(s"Fetching data from cache.")

        context.self ! Response(uuid, request, cachedResult)
      } else {
        databaseWorkerPool ! request
      }
    } else {
      databaseWorkerPool ! request
    }
  }

  // Saves response to the cache
  def processResponse(response: Response) = {
    val requestHash = response.request.hashCode().toString
    val result = response.result

    // TODO: make a set of "cacheable" methods
    val cachedResult = cacheClient.get(requestHash)
    if (cachedResult == null) {
      cacheClient.set(requestHash, 3600, result)
    }
  }

  def receive = {
    case req @ Request(uuid, request) => {
      processRequest(req)
    }
    case res @ Response(uuid, request, result) => {
      processResponse(res)
      master ! res
    }
  }
}
