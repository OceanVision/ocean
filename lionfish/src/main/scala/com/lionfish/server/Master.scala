package com.lionfish.server

import akka.actor.{Actor, ActorRef, ActorSystem, Props}
import akka.routing.RoundRobinPool
import akka.event.Logging
import com.lionfish.messages._

class Master extends Actor {
  val log = Logging(context.system, this)
  log.info("Master is running.")

  var senderMap: Map[String, ActorRef] = Map()

  // Creates request handler system and pool
  private val requestHandlerSystem = ActorSystem("masterSystem")
  private val requestHandlerPool = requestHandlerSystem.actorOf(
    Props[RequestHandler].withRouter(RoundRobinPool(10)), "requestHandlerPool")

  def receive = {
    case req @ Request(connectionUuid, request) => {
      senderMap += connectionUuid -> sender
      requestHandlerPool ! req
    }
    case Response(connectionUuid, result) => {
      // TODO: error handling
      senderMap(connectionUuid) ! result
      senderMap -= connectionUuid
    }
  }
}
