package com.lionfish.server

import akka.actor.{Actor, ActorRef, ActorSystem, Props}
import akka.event.Logging
import com.lionfish.messages._

class Proxy extends Actor {
  val log = Logging(context.system, this)
  log.info("Proxy is running.")

  private var senderRefs: Map[String, ActorRef] = Map()

  // Creates master worker
  private val masterSystem = ActorSystem("masterSystem")
  private val master = masterSystem.actorOf(Props(new Master(context.self)))

  def receive = {
    case req @ Request(clientUuid, request) => {
      senderRefs += clientUuid -> sender
      master ! req
    }
    case Response(clientUuid, result) => {
      senderRefs(clientUuid) ! result
      senderRefs -= clientUuid
    }
  }
}
