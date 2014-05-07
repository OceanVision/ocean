package com.lionfish.client

import scala.collection.mutable.ListBuffer

class Batch(implicit private val client: Client) extends AnyRef {
  private var tasks: Map[String, Any] = Map()
  private var count: Int = 0

  def append(f: Method) = {
    val data = f.getRequest.asInstanceOf[Map[String, Any]]
    val funcName = data("funcName").asInstanceOf[String]

    if (!tasks.contains(funcName)) {
      tasks += funcName -> ListBuffer(List(data("args"), count))
    } else {
      var buffer = tasks(funcName).asInstanceOf[ListBuffer[List[Any]]]
      buffer += List(data("args"), count)
    }

    count += 1
  }

  def +=(f: Method): Batch = {
    append(f)
    this
  }

  def submit(): List[Any] = {
    val request = Map("tasks" -> tasks, "count" -> count)

    client.send(request)
    val result = client.receive[List[Any]]()

    tasks = Map()
    count = 0

    result
  }
}
