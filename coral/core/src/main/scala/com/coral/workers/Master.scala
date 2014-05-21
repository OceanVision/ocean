package com.coral.workers

import akka.actor._
import akka.routing._
import com.typesafe.config.ConfigFactory
import com.coral.messages._

// TODO: Use akka configuration!

class Master extends Actor {
  private val databaseWorkerSystemPort = 7781
  private var senderMap: Map[String, ActorRef] = Map()

  // Database worker pool system
  private val databaseWorkerPath =
    s"akka.tcp://databaseWorkerSystem@localhost:$databaseWorkerSystemPort/user/databaseWorkerPool"
  val databaseWorkerPool = context.actorSelection(databaseWorkerPath)

  // Decides whether data should be fetched from database or Memcached
  def processRequest(request: Request) = {
    databaseWorkerPool ! request
  }

  def receive = {
    case req @ Request(uuid, request) => {
      // Master stores a remote reference of the request handler for a while
      senderMap += uuid -> sender
      processRequest(req)
    }
    case res @ Response(uuid, result) => {
      // A result is being returned to the request handler
      senderMap(uuid) ! res
      senderMap -= uuid
    }
  }
}
