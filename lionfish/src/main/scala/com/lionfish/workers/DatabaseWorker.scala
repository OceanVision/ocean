package com.lionfish.workers

import scala.collection.mutable.ListBuffer
import akka.actor.Actor
import com.lionfish.messages._
import com.lionfish.logging.Logging
import com.lionfish.wrappers._

class DatabaseWorker(private val wrapper: DatabaseWrapper) extends Worker with Actor {
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
            rawResult = wrapper.executeQuery(fullArgs.toList)
          }
          case "getByUuid" => {
            rawResult = wrapper.getByUuid(fullArgs.toList)
          }
          case "getByLink" => {
            rawResult = wrapper.getByLink(fullArgs.toList)
          }
          case "getByTag" => {
            rawResult = wrapper.getByTag(fullArgs.toList)
          }
          case "getByUsername" => {
            rawResult = wrapper.getByUsername(fullArgs.toList)
          }
          case "getByLabel" => {
            rawResult = wrapper.getByLabel(fullArgs.toList)
          }
          case "getModelNodes" => {
            rawResult = wrapper.getModelNodes(fullArgs.toList)
          }
          case "getChildren" => {
            rawResult = wrapper.getChildren(fullArgs.toList)
          }
          case "getInstances" => {
            rawResult = wrapper.getInstances(fullArgs.toList)
          }
          case "getUserFeeds" => {
            rawResult = wrapper.getUserFeeds(fullArgs.toList)
          }
          case "setLabel" => {
            rawResult = wrapper.setLabel(fullArgs.toList)
          }
          case "deleteLabel" => {
            rawResult = wrapper.deleteLabel(fullArgs.toList)
          }
          case "setProperties" => {
            rawResult = wrapper.setProperties(fullArgs.toList)
          }
          case "deleteProperties" => {
            rawResult = wrapper.deleteProperties(fullArgs.toList)
          }
          case "createModelNodes" => {
            rawResult = wrapper.createModelNodes(fullArgs.toList)
          }
          case "createNodes" => {
            rawResult = wrapper.createNodes(fullArgs.toList)
          }
          case "deleteNodes" => {
            rawResult = wrapper.deleteNodes(fullArgs.toList)
          }
          case "createRelationships" => {
            rawResult = wrapper.createRelationships(fullArgs.toList)
          }
          case "createUniqueRelationships" => {
            rawResult = wrapper.createUniqueRelationships(fullArgs.toList)
          }
          case "deleteRelationships" => {
            rawResult = wrapper.deleteRelationships(fullArgs.toList)
          }
          case "setRelationshipProperties" => {
            rawResult = wrapper.setRelationshipProperties(fullArgs.toList)
          }
          case "deleteRelationshipProperties" => {
            rawResult = wrapper.deleteRelationshipProperties(fullArgs.toList)
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
            rawResult = wrapper.executeQuery(args)
          }
          case "getByUuid" => {
            rawResult = wrapper.getByUuid(args)
          }
          case "getByLink" => {
            rawResult = wrapper.getByLink(args)
          }
          case "getByTag" => {
            rawResult = wrapper.getByTag(args)
          }
          case "getByUsername" => {
            rawResult = wrapper.getByUsername(args)
          }
          case "getByLabel" => {
            rawResult = wrapper.getByLabel(args)
          }
          case "getModelNodes" => {
            rawResult = wrapper.getModelNodes(args)
          }
          case "getChildren" => {
            rawResult = wrapper.getChildren(args)
          }
          case "getInstances" => {
            rawResult = wrapper.getInstances(args)
          }
          case "getUserFeeds" => {
            rawResult = wrapper.getUserFeeds(args)
          }
          case "setLabel" => {
            rawResult = wrapper.setLabel(args)
          }
          case "deleteLabel" => {
            rawResult = wrapper.deleteLabel(args)
          }
          case "setProperties" => {
            rawResult = wrapper.setProperties(args)
          }
          case "deleteProperties" => {
            rawResult = wrapper.deleteProperties(args)
          }
          case "createModelNodes" => {
            rawResult = wrapper.createModelNodes(args)
          }
          case "createNodes" => {
            rawResult = wrapper.createNodes(args)
          }
          case "deleteNodes" => {
            rawResult = wrapper.deleteNodes(args)
          }
          case "createRelationships" => {
            rawResult = wrapper.createRelationships(args)
          }
          case "createUniqueRelationships" => {
            rawResult = wrapper.createUniqueRelationships(args)
          }
          case "deleteRelationships" => {
            rawResult = wrapper.deleteRelationships(args)
          }
          case "setRelationshipProperties" => {
            rawResult = wrapper.setRelationshipProperties(args)
          }
          case "deleteRelationshipProperties" => {
            rawResult = wrapper.deleteRelationshipProperties(args)
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
