package com.coral.actors

import akka.actor._
import akka.routing._
import com.typesafe.config.ConfigFactory
import com.coral.messages._

// TODO: Use akka configuration!

class Master extends Actor {
  private var senderMap: Map[String, ActorRef] = Map()
  val lionfishWorkerSystem = ActorSystem(
    "lionfishWorkerSystem", ConfigFactory.load("lionfishWorkerSystem"))
  val lionfishWorkerPool = lionfishWorkerSystem.actorOf(
    Props[LionfishWorker].withRouter(RoundRobinPool(5)), "lionfishWorkerPool")

  def receive = {
    case Request(uuid, request) => {
      // Master stores a remote reference to a request handler for a while
      senderMap += uuid -> sender
      lionfishWorkerPool ! Request(uuid, request)
    }
    case Result(uuid, result) => {
      // A result is being returned to a request handler
      senderMap(uuid) ! Result(uuid, result)
      senderMap -= uuid
    }
  }
}
