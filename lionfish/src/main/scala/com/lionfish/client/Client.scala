package com.lionfish.client

import java.net.Socket
import com.lionfish.utils.{Factory, IO}

class Client extends Factory {
  implicit val client = this
  private val host = "localhost" // TODO: create a config file
  private val port = 21
  private implicit var socket: Socket = null
  println(s"Connected to $host:$port.")

  def connect() = {
    socket = new Socket(host, port)
  }

  def disconnect() = {
    try {
      socket.close()
      println(s"Disconnected from the Lionfish server.")
    } catch {
      case e: Exception => {
        println(s"Failed to disconnect with server. Error message: $e")
      }
    }
  }

  def send(rawData: Any) = {
    IO.send(rawData)
  }

  def receive[T: Manifest](): T = {
    IO.receive[T]()
  }

  def getBatch: Batch = {
    if (socket != null) {
      new Batch
    } else {
      throw new Exception("The client is not connected to the Lionfish server.")
    }
  }

  case class getByUuid(private val nodeUuid: String) extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "getByUuid",
        "args" -> Map(
          "uuid" -> nodeUuid
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[Map[String, Any]]()
    }
  }

  case class getByLink(private val modelName: String, link: String) extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "getByLink",
        "args" -> Map(
          "modelName" -> modelName,
          "link" -> link
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[Map[String, Any]]()
    }
  }

  case class getModelNodes() extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "getModelNodes",
        "args" -> Map()
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[List[Map[String, Any]]]()
    }
  }

  case class getChildren(private val parentUuid: String, relType: String,
                         childrenProps: Map[String, Any] = Map()) extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "getChildren",
        "args" -> Map(
          "parentUuid" -> parentUuid,
          "relType" -> relType,
          "childrenProps" -> childrenProps
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[List[Map[String, Any]]]()
    }
  }

  case class getInstances(private val modelName: String,
                          childrenProps: Map[String, Any] = Map()) extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "getInstances",
        "args" -> Map(
          "modelName" -> modelName,
          "childrenProps" -> childrenProps
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[List[Map[String, Any]]]()
    }
  }

  @deprecated(message = "Use setProperties instead.")
  case class set(private val uuid: String, props: Map[String, Any]) extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "set",
        "args" -> Map(
          "uuid" -> uuid,
          "props" -> props
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[Any]()
    }
  }

  case class setProperties(private val uuid: String, props: Map[String, Any]) extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "set",
        "args" -> Map(
          "uuid" -> uuid,
          "props" -> props
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[Any]()
    }
  }

  case class createNode(private val modelName: String, relType: String,
                        props: Map[String, Any]) extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "createNodes",
        "args" -> Map(
          "modelName" -> modelName,
          "relType" -> relType,
          "props" -> props
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[Map[String, Any]]()
    }
  }

  case class deleteNode(private val nodeUuid: String) extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "deleteNodes",
        "args" -> Map(
          "uuid" -> nodeUuid
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[Any]()
    }
  }

  case class createRelationship(private val startNodeUuid: String, endNodeUuid: String,
                                relType: String, props: Map[String, Any] = Map()) extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "createRelationships",
        "args" -> Map(
          "startNodeUuid" -> startNodeUuid,
          "endNodeUuid" -> endNodeUuid,
          "relType" -> relType,
          "props" -> props
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[Any]()
    }
  }

  case class deleteRelationship(private val startNodeUuid: String, endNodeUuid: String)
    extends Method {
    override def method(getOnlyRequest: Boolean = false): Any = {
      val request = Map(
        "funcName" -> "deleteRelationships",
        "args" -> Map(
          "startNodeUuid" -> startNodeUuid,
          "endNodeUuid" -> endNodeUuid
        )
      )

      if (getOnlyRequest) {
        return request
      }

      send(request)
      receive[Any]()
    }
  }
}
