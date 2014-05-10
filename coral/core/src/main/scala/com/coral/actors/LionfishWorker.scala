package com.coral.actors

import akka.actor._
import com.coral.messages._
import com.lionfish.client.Client

class LionfishWorker extends Actor {
  private val lionfishClient = new Client
  lionfishClient.connect()

  private def getFeedList(clientId: String): List[Map[String, Any]] = {
    val modelName = "ContentSource"
    val result = lionfishClient.getInstances(modelName).run()
      .asInstanceOf[List[Map[String, Any]]]
    result
  }

  private def processRequest(request: Map[String, Any]): Any = {
    val coralMethodName = request("coralMethodName").asInstanceOf[String]
    val requestData = request("data").asInstanceOf[Map[String, Any]]

    var result: Any = null
    coralMethodName match {
      case "getFeedList" => {
        val clientId = requestData("clientId").asInstanceOf[String]
        result = getFeedList(clientId)
      }
    }
    result
  }

  def receive = {
    case Request(uuid, request) => {
      val result = processRequest(request)
      sender ! Result(uuid, result)
    }
  }
}
