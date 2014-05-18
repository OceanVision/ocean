package com.lionfish.server

import akka.actor.{Actor, ActorRef, ActorSystem, Props}
import akka.routing.RoundRobinPool
import akka.event.Logging
import com.lionfish.messages._

class Master(private val proxy: ActorRef) extends Actor {
  val log = Logging(context.system, this)
  log.info("Master is running.")

  // Creates request handler system and pool
  private val requestHandlerSystem = ActorSystem("masterSystem")
  private val requestHandlerPool = requestHandlerSystem.actorOf(
    Props[RequestHandler].withRouter(RoundRobinPool(10)), "requestHandlerPool")

  def receive = {
    case req @ Request(clientUuid, request) => {
      requestHandlerPool ! req
    }
    case res @ Response(clientUuid, result) => {
      proxy ! res
    }
  }
}
