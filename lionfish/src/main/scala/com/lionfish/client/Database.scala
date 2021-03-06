package com.lionfish.client

import akka.actor._
import com.typesafe.config.ConfigFactory
import com.lionfish.utils.Config

object Database extends Factory {
  private var serverAddress = Config.defaultServerAddress
  private var serverPort = Config.defaultServerPort

  def getServerAddress = {
    serverAddress
  }

  def getServerPort = {
    serverPort
  }

  def setServerAddress(address: String) = {
    serverAddress = address
  }

  def setServerPort(port: Int) = {
    serverPort = port
  }

  def getBatchStream: Stream = {
    new BatchStream(serverAddress, serverPort)
  }

  def getSequenceStream: Stream = {
    new SequenceStream(serverAddress, serverPort)
  }

  case class getByUuid(private val nodeUuid: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getByUuid",
        "args" -> Map(
          "uuid" -> nodeUuid
        )
      )

      request
    }
  }

  case class getByLink(private val modelName: String, link: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getByLink",
        "args" -> Map(
          "modelName" -> modelName,
          "link" -> link
        )
      )

      request
    }
  }

  case class getByTag(private val tag: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getByTag",
        "args" -> Map(
          "tag" -> tag
        )
      )

      request
    }
  }

  case class getByLabel(private val label: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getByLabel",
        "args" -> Map(
          "label" -> label
        )
      )

      request
    }
  }

  case class getModelNodes() extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getModelNodes",
        "args" -> Map()
      )

      request
    }
  }

  case class getChildren(private val parentUuid: String, relationshipType: String,
                         childrenProperties: Map[String, Any] = Map(),
                         relationshipProperties: Map[String, Any] = Map()) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getChildren",
        "args" -> Map(
          "parentUuid" -> parentUuid,
          "relType" -> relationshipType,
          "childrenProps" -> childrenProperties,
          "relProps" -> relationshipProperties
        )
      )

      request
    }
  }

  case class getInstances(private val modelName: String,
                          childrenProperties: Map[String, Any] = Map(),
                          relationshipProperties: Map[String, Any] = Map()) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getInstances",
        "args" -> Map(
          "modelName" -> modelName,
          "childrenProps" -> childrenProperties,
          "relProps" -> relationshipProperties
        )
      )

      request
    }
  }

  case class getUserFeeds(private val uuid: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getUserFeeds",
        "args" -> Map(
          "uuid" -> uuid
        )
      )

      request
    }
  }

  case class setLabel(private val uuid: String, label: String)
    extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "setLabel",
        "args" -> Map(
          "uuid" -> uuid,
          "label" -> label
        )
      )

      request
    }
  }

  case class deleteLabel(private val uuid: String, label: String)
    extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "deleteLabel",
        "args" -> Map(
          "uuid" -> uuid,
          "label" -> label
        )
      )

      request
    }
  }

  case class setProperties(private val uuid: String, properties: Map[String, Any])
    extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "setProperties",
        "args" -> Map(
          "uuid" -> uuid,
          "props" -> properties
        )
      )

      request
    }
  }

  case class deleteProperties(private val uuid: String, propertyKeys: List[String])
    extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "deleteProperties",
        "args" -> Map(
          "uuid" -> uuid,
          "propKeys" -> propertyKeys
        )
      )

      request
    }
  }

  case class createModelNode(private val modelName: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "createModelNodes",
        "args" -> Map(
          "modelName" -> modelName
        )
      )

      request
    }
  }

  case class createNode(private val modelName: String, relationshipType: String,
                        properties: Map[String, Any]) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "createNodes",
        "args" -> Map(
          "modelName" -> modelName,
          "relType" -> relationshipType,
          "props" -> properties
        )
      )

      request
    }
  }

  case class deleteNode(private val uuid: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "deleteNodes",
        "args" -> Map(
          "uuid" -> uuid
        )
      )

      request
    }
  }

  case class createRelationship(private val startNodeUuid: String, endNodeUuid: String,
                                relationshipType: String, properties: Map[String, Any] = Map())
    extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "createRelationships",
        "args" -> Map(
          "startNodeUuid" -> startNodeUuid,
          "endNodeUuid" -> endNodeUuid,
          "type" -> relationshipType,
          "props" -> properties
        )
      )

      request
    }
  }

  case class deleteRelationship(private val startNodeUuid: String, endNodeUuid: String)
    extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "deleteRelationships",
        "args" -> Map(
          "startNodeUuid" -> startNodeUuid,
          "endNodeUuid" -> endNodeUuid
        )
      )

      request
    }
  }

  case class setRelationshipProperties(private val startNodeUuid: String, endNodeUuid: String,
                                       properties: Map[String, Any])
    extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "setRelationshipProperties",
        "args" -> Map(
          "startNodeUuid" -> startNodeUuid,
          "endNodeUuid" -> endNodeUuid,
          "props" -> properties
        )
      )

      request
    }
  }

  case class deleteRelationshipProperties(private val startNodeUuid: String, endNodeUuid: String,
                                          propertyKeys: List[String])
    extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "deleteRelationshipProperties",
        "args" -> Map(
          "startNodeUuid" -> startNodeUuid,
          "endNodeUuid" -> endNodeUuid,
          "propKeys" -> propertyKeys
        )
      )

      request
    }
  }
}
