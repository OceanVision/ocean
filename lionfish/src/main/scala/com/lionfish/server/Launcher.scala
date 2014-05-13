package com.lionfish.server

import akka.actor._
import com.typesafe.config.ConfigFactory

object Launcher {
  def main(args: Array[String]) = {
    // Creates remote proxy worker
    val proxySystem = ActorSystem("proxySystem", ConfigFactory.load("proxySystem"))
    proxySystem.actorOf(Props(new Proxy), "proxy")
  }
}
