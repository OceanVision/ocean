package com.lionfish.server

import java.net.Socket
import scala.collection.mutable.ListBuffer
//import akka.actor._
//import com.lionfish.messages._
import com.lionfish.utils.IO

class RequestHandler(private val id: Int, socket: Socket) extends Runnable {
  println(s"Client $id connected.")

  private def disconnect() = {
    try {
      socket.close()
      println(s"Client $id disconnected.")
    } catch {
      case e: Exception => {
        println(s"Client $id failed to disconnect. Error message: $e")
      }
    }
  }

  private def executeBatch(request: Map[String, Any]): List[Any] = {
    try {
      val count = request("count").asInstanceOf[Int]
      val tasks = request("tasks").asInstanceOf[Map[String, List[List[Any]]]]

      var response: List[Any] = List.fill(count.toInt)(null)
      for ((methodName, params) <- tasks) {
        var fullArgs: ListBuffer[Map[String, Any]] = ListBuffer()
        for (item <- params) {
          fullArgs += item(0).asInstanceOf[Map[String, Any]]
        }

        println(s"Client $id executes $methodName in batch.")

        // TODO: Solve this with reflection
        var rawResult: List[Any] = null
        methodName match {
          case "getByUuid" => {
            rawResult = DatabaseManager.getByUuid(fullArgs.toList)
          }
          case "getByLink" => {
            rawResult = DatabaseManager.getByLink(fullArgs.toList)
          }
          case "getModelNodes" => {
            rawResult = DatabaseManager.getModelNodes(fullArgs.toList)
          }
          case "getChildren" => {
            rawResult = DatabaseManager.getChildren(fullArgs.toList)
          }
          case "getInstances" => {
            rawResult = DatabaseManager.getInstances(fullArgs.toList)
          }
          case "setProperties" => {
            rawResult = DatabaseManager.setProperties(fullArgs.toList)
          }
          case "deleteProperties" => {
            rawResult = DatabaseManager.deleteProperties(fullArgs.toList)
          }
          case "createNodes" => {
            rawResult = DatabaseManager.createNodes(fullArgs.toList)
          }
          case "deleteNodes" => {
            rawResult = DatabaseManager.deleteNodes(fullArgs.toList)
          }
          case "createRelationships" => {
            rawResult = DatabaseManager.createRelationships(fullArgs.toList)
          }
          case "deleteRelationships" => {
            rawResult = DatabaseManager.deleteRelationships(fullArgs.toList)
          }
          case "setRelationshipProperties" => {
            rawResult = DatabaseManager.setRelationshipProperties(fullArgs.toList)
          }
          case "deleteRelationshipProperties" => {
            rawResult = DatabaseManager.deleteRelationshipProperties(fullArgs.toList)
          }
          case _ => throw new NoSuchMethodException(methodName)
        }

        if (rawResult != null) {
          for (i <- 0 to rawResult.length - 1) {
            response = response.updated(params(i)(1).asInstanceOf[Int], rawResult(i))
          }
        }
      }

      response
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Client $id failed to execute a batch at line $line. Error message: $e")
      }
      List()
    }
  }

  private def executeSequence(request: Map[String, Any]): Any = {
    try {
      val tasks = request("tasks").asInstanceOf[List[Map[String, Any]]]

      var response: ListBuffer[Any] = ListBuffer()
      for (item <- tasks) {
        val methodName = item("methodName").asInstanceOf[String]
        val args = List(item("args").asInstanceOf[Map[String, Any]])

        println(s"Client $id executes $methodName.")

        // TODO: Solve this with reflection
        var rawResult: List[Any] = null
        methodName match {
          case "getByUuid" => {
            rawResult = DatabaseManager.getByUuid(args)
          }
          case "getByLink" => {
            rawResult = DatabaseManager.getByLink(args)
          }
          case "getModelNodes" => {
            rawResult = DatabaseManager.getModelNodes(args)
          }
          case "getChildren" => {
            rawResult = DatabaseManager.getChildren(args)
          }
          case "getInstances" => {
            rawResult = DatabaseManager.getInstances(args)
          }
          case "setProperties" => {
            rawResult = DatabaseManager.setProperties(args)
          }
          case "deleteProperties" => {
            rawResult = DatabaseManager.deleteProperties(args)
          }
          case "createNodes" => {
            rawResult = DatabaseManager.createNodes(args)
          }
          case "deleteNodes" => {
            rawResult = DatabaseManager.deleteNodes(args)
          }
          case "createRelationships" => {
            rawResult = DatabaseManager.createRelationships(args)
          }
          case "deleteRelationships" => {
            rawResult = DatabaseManager.deleteRelationships(args)
          }
          case "setRelationshipProperties" => {
            rawResult = DatabaseManager.setRelationshipProperties(args)
          }
          case "deleteRelationshipProperties" => {
            rawResult = DatabaseManager.deleteRelationshipProperties(args)
          }
          case _ => throw new NoSuchMethodException(methodName)
        }

        if (rawResult != null && rawResult.length > 0) {
          response += rawResult(0)
        } else {
          response += null
        }
      }

      response.toList
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Client $id failed to execute a function at line $line. Error message: $e")
      }
      null
    }
  }

  def run() = {
    // Process requests
    var request: Map[String, Any] = null
    while ({request = IO.receive[Map[String, Any]](); request} != null) {
      try {
        var response: Any = null
        val requestType = request("type").asInstanceOf[String]
        if (requestType == "sequence") {
          response = executeSequence(request)
        } else {
          //println(s"$request")
          response = executeBatch(request)
        }

        //println(s"$response")
        IO.send(response)
      }
    }

    disconnect()
  }
}
