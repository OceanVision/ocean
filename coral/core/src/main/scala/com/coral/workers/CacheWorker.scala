package com.coral.workers

import java.net.InetSocketAddress
import scala.util.Random
import akka.actor._
import net.spy.memcached.MemcachedClient
import com.coral.messages._
import com.coral.utils.Config

class CacheWorker extends Actor {
  private val masterSystemPort = Config.masterSystemPort
  private val databaseWorkerSystemPort = Config.databaseWorkerSystemPort
  private val cacheClient = new MemcachedClient(new InetSocketAddress("127.0.0.1", Config.cachePort))

  // Master worker
  private val masterWorkerPath =
    s"akka.tcp://masterSystem@localhost:$masterSystemPort/user/master"
  private val masterWorker = context.actorSelection(masterWorkerPath)

  // Database worker pool system
  private val databaseWorkerPath =
    s"akka.tcp://databaseWorkerSystem@localhost:$databaseWorkerSystemPort/user/databaseWorkerPool"
  private val databaseWorkerPool = context.actorSelection(databaseWorkerPath)

  // Decides whether fetch data from cache or database
  def processRequest(request: Request) = {
    val requestHash = request.request.hashCode().toString

    val cachedResult = cacheClient.get(requestHash)
    if (cachedResult != null) {
      // If data exists in the cache
      val uuid = request.uuid
      val coralMethodName = request.request("coralMethodName").asInstanceOf[String]
      println(s"Fetching $coralMethodName request from cache.")

      context.self ! Response(uuid, request.request, cachedResult)
    } else {
      databaseWorkerPool ! request
    }
  }

  // Saves response to the cache
  def processResponse(response: Response) = {
    val coralMethodName = response.request("coralMethodName").asInstanceOf[String]
    val requestHash = response.request.hashCode().toString
    val result = response.result

    // TODO: make a set of "cacheable" methods
    val cachedResult = cacheClient.get(requestHash)
    if (coralMethodName == "getFeedList" && cachedResult == null) {
      cacheClient.set(requestHash, 3600, result)
    }
  }

  def receive = {
    case req @ Request(uuid, request) => {
      processRequest(req)
    }
    case res @ Response(uuid, request, result) => {
      processResponse(res)
      masterWorker ! res
    }
  }
}
