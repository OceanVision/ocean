package com.lionfish.client

import scala.collection.mutable.ListBuffer
import scala.concurrent.Await
import scala.concurrent.duration._
import akka.actor._
import akka.pattern.ask
import akka.util.Timeout
import com.lionfish.messages.Request

// Abstract command
trait Method {
  private implicit val timeout = Timeout(600 seconds)
  var tasks: ListBuffer[Map[String, Any]] = ListBuffer(getRequest)

  // Template method
  protected def getRequest: Map[String, Any]

  protected def execute(request: Map[String, Any])
                       (implicit proxy: ActorSelection, streamUuid: String): Any = {
    val future = proxy ? Request(streamUuid, request)
    Await.result[Any](future, timeout.duration)
  }

  def <<(method: Method): Method = {
    tasks ++= method.tasks
    this
  }

  def executeSequence()(implicit proxy: ActorSelection, streamUuid: String): Any = {
    val finalRequest: Map[String, Any] = Map(
      "type" -> "sequence",
      "tasks" -> tasks.toList
    )

    execute(finalRequest)
  }

  def executeBatch()(implicit proxy: ActorSelection, streamUuid: String): List[Any] = {
    var groupedTasks: scala.collection.mutable.Map[String, List[List[Any]]] =
      scala.collection.mutable.Map()
    var count = 0

    for (item <- tasks) {
      val methodName = item("methodName").asInstanceOf[String]
      val args = item("args").asInstanceOf[Map[String, Any]]

      if (!groupedTasks.contains(methodName)) {
        groupedTasks += methodName -> List(List(args, count))
      } else {
        groupedTasks(methodName) = groupedTasks(methodName) :+ List(args, count)
      }

      count += 1
    }

    val finalRequest: Map[String, Any] = Map(
      "type" -> "batch",
      "count" -> count,
      "tasks" -> groupedTasks.toMap
    )

    execute(finalRequest).asInstanceOf[List[Any]]
  }
}
