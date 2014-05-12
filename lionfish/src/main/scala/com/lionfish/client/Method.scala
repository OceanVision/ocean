package com.lionfish.client

import java.net.Socket
import scala.collection.mutable.ListBuffer
import com.lionfish.utils.IO

// Abstract command
trait Method {
  var tasks: ListBuffer[Map[String, Any]] = ListBuffer(getRequest)

  // Template method
  protected def getRequest: Map[String, Any]

  protected def send(request: Map[String, Any])(implicit socket: Socket) = {
    IO.send(request)
  }

  protected def receive[T: Manifest]()(implicit socket: Socket): T = {
    IO.receive[T]()
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

    send(finalRequest)
    receive[Any]()
  }

  def executeBatch()(implicit socket: Socket): List[Any] = {
    var groupedTasks: Map[String, Any] = Map()
    var count = 0

    for (item <- tasks) {
      val methodName = item("methodName").asInstanceOf[String]
      val args = item("args").asInstanceOf[Map[String, Any]]

      if (!groupedTasks.contains(methodName)) {
        groupedTasks += methodName -> ListBuffer(List(args, count))
      } else {
        var buffer = groupedTasks(methodName).asInstanceOf[ListBuffer[List[Any]]]
        buffer += List(args, count)
      }

      count += 1
    }

    val finalRequest: Map[String, Any] = Map(
      "type" -> "batch",
      "count" -> count,
      "tasks" -> groupedTasks
    )

    send(finalRequest)
    receive[List[Any]]()
  }
}
