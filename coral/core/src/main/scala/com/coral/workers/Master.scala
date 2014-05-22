package com.coral.workers

import akka.actor._
import akka.routing._
import com.typesafe.config.ConfigFactory
import com.coral.messages._
import com.coral.utils.Config

// TODO: Use akka configuration!

class Master extends Actor {
  private val cacheWorkerSystemPort = Config.cacheWorkerSystemPort
  private var senderMap: Map[String, ActorRef] = Map()

  // Database worker pool system
  private val cacheWorkerPath =
    s"akka.tcp://cacheWorkerSystem@localhost:$cacheWorkerSystemPort/user/cacheWorkerPool"
  private val cacheWorkerPool = context.actorSelection(cacheWorkerPath)

  def processRequest(request: Request) = {
    cacheWorkerPool ! request
  }

  def receive = {
    case req @ Request(uuid, request) => {
      // Master stores a remote reference of the request handler for a while
      senderMap += uuid -> sender
      processRequest(req)
    }
    case res @ Response(uuid, request, result) => {
      // The result is being returned to the request handler
      senderMap(uuid) ! res
      senderMap -= uuid
    }
  }
}
