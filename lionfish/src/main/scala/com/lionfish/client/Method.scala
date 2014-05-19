package com.lionfish.client

import java.net.Socket
import scala.collection.mutable.ListBuffer
import com.lionfish.utils._

// Abstract command
trait Method {
  var tasks: ListBuffer[Map[String, Any]] = ListBuffer(getRequest)

  // Template method
  protected def getRequest: Map[String, Any]

  protected def execute(request: Map[String, Any])(implicit socket: Socket): Any = {
    IO.send(request)
    IO.receive[Any]()
  }

  def <<(method: Method): Method = {
    tasks ++= method.tasks
    this
  }

  def executeSequence()(implicit socket: Socket): Any = {
    val finalRequest: Map[String, Any] = Map(
      "type" -> "sequence",
      "tasks" -> tasks.toList
    )

    execute(finalRequest)
  }

  def executeBatch()(implicit socket: Socket): List[Any] = {
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
