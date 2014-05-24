package com.lionfish.workers

import akka.actor.{Actor, ActorRef}
import akka.event.Logging
import com.lionfish.utils.Config
import com.lionfish.messages._

class Master extends Actor {
  private val log = Logging(context.system, this)

  private val cacheWorkerSystemPort = Config.cacheWorkerSystemPort
  private var senderMap: Map[String, ActorRef] = Map()

  // Cache worker pool system
  private val cacheWorkerPath =
    s"akka.tcp://cacheWorkerSystem@localhost:$cacheWorkerSystemPort/user/cacheWorkerPool"
  private val cacheWorkerPool = context.actorSelection(cacheWorkerPath)

  def receive = {
    case req @ Request(connectionUuid, request) => {
      senderMap += connectionUuid -> sender
      cacheWorkerPool ! req
    }
    case Response(connectionUuid, request, result) => {
      // TODO: error handling
      senderMap(connectionUuid) ! result
      senderMap -= connectionUuid
    }
  }
}
