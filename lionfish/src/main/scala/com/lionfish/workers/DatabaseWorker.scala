package com.lionfish.workers

import scala.collection.mutable.ListBuffer
import akka.actor.Actor
import com.lionfish.messages._
import com.lionfish.logging.Logging

class DatabaseWorker extends Worker with Actor {
  private val log = Logging

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

        log.info(s"Executing $methodName in a batch.")

        // TODO: Solve this with reflection
        var rawResult: List[Any] = null
        methodName match {
          case "executeQuery" => {
            rawResult = DatabaseManager.executeQuery(fullArgs.toList)
          }
          case "getByUuid" => {
            rawResult = DatabaseManager.getByUuid(fullArgs.toList)
          }
          case "getByLink" => {
            rawResult = DatabaseManager.getByLink(fullArgs.toList)
          }
          case "getByTag" => {
            rawResult = DatabaseManager.getByTag(fullArgs.toList)
          }
          case "getByUsername" => {
            rawResult = DatabaseManager.getByUsername(fullArgs.toList)
          }
          case "getByLabel" => {
            rawResult = DatabaseManager.getByLabel(fullArgs.toList)
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
          case "getUserFeeds" => {
            rawResult = DatabaseManager.getUserFeeds(fullArgs.toList)
          }
          case "setLabel" => {
            rawResult = DatabaseManager.setLabel(fullArgs.toList)
          }
          case "deleteLabel" => {
            rawResult = DatabaseManager.deleteLabel(fullArgs.toList)
          }
          case "setProperties" => {
            rawResult = DatabaseManager.setProperties(fullArgs.toList)
          }
          case "deleteProperties" => {
            rawResult = DatabaseManager.deleteProperties(fullArgs.toList)
          }
          case "createModelNodes" => {
            rawResult = DatabaseManager.createModelNodes(fullArgs.toList)
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
          case "createUniqueRelationships" => {
            rawResult = DatabaseManager.createUniqueRelationships(fullArgs.toList)
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
        log.error(s"Failed to execute a batch. Error message: $e")
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

        log.info(s"Executing $methodName in a sequence.")

        // TODO: Solve this with reflection
        var rawResult: List[Any] = null
        methodName match {
          case "executeQuery" => {
            rawResult = DatabaseManager.executeQuery(args)
          }
          case "getByUuid" => {
            rawResult = DatabaseManager.getByUuid(args)
          }
          case "getByLink" => {
            rawResult = DatabaseManager.getByLink(args)
          }
          case "getByTag" => {
            rawResult = DatabaseManager.getByTag(args)
          }
          case "getByUsername" => {
            rawResult = DatabaseManager.getByUsername(args)
          }
          case "getByLabel" => {
            rawResult = DatabaseManager.getByLabel(args)
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
          case "getUserFeeds" => {
            rawResult = DatabaseManager.getUserFeeds(args)
          }
          case "setLabel" => {
            rawResult = DatabaseManager.setLabel(args)
          }
          case "deleteLabel" => {
            rawResult = DatabaseManager.deleteLabel(args)
          }
          case "setProperties" => {
            rawResult = DatabaseManager.setProperties(args)
          }
          case "deleteProperties" => {
            rawResult = DatabaseManager.deleteProperties(args)
          }
          case "createModelNodes" => {
            rawResult = DatabaseManager.createModelNodes(args)
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
          case "createUniqueRelationships" => {
            rawResult = DatabaseManager.createUniqueRelationships(args)
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
        log.error(s"Failed to execute a sequence. Error message: $e")
      }
        List()
    }
  }

  override def processRequest(request: Request): Any = {
    val requestData = request.request

    // Processes request
    try {
      var result: Any = null
      val requestType = requestData("type").asInstanceOf[String]
      if (requestType == "sequence") {
        result = executeSequence(requestData)
      } else {
        result = executeBatch(requestData)
      }

      result
    } catch {
      case e: Exception => {
        log.error(s"Failed to process a request. Error message: $e")
      }
        List()
    }
  }

  def receive = {
    case req @ Request(connectionUuid, request) => {
      val result = processRequest(req)
      sender ! Response(connectionUuid, req, result)
    }
  }
}
