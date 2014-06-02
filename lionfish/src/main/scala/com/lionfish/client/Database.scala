package com.lionfish.client

import akka.actor._
import com.typesafe.config.ConfigFactory
import com.lionfish.utils.Config

object Database extends Factory {
  private var serverAddress = Config.serverAddress
  private var serverPort = Config.serverPort

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

  /**
   * Executes Cypher query
   * @return list of lists of data
   */
  case class executeQuery(private val query: String,
                          private val parameters: Map[String, Any]) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "executeQuery",
        "args" -> Map(
          "query" -> query,
          "parameters" -> parameters
        )
      )

      request
    }
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

  case class getByLink(private val modelName: String,
                       private val link: String) extends Method {
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

  case class getByUsername(private val username: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getByUsername",
        "args" -> Map(
          "username" -> username
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

  case class getChildren(private val parentUuid: String,
                         private val relationshipType: String,
                         private val childrenProperties: Map[String, Any] = Map(),
                         private val relationshipProperties: Map[String, Any] = Map(),
                         private val limit: Int = 0) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getChildren",
        "args" -> Map(
          "parentUuid" -> parentUuid,
          "relType" -> relationshipType,
          "childrenProps" -> childrenProperties,
          "relProps" -> relationshipProperties,
          "limit" -> limit
        )
      )

      request
    }
  }

  case class getInstances(private val modelName: String,
                          private val childrenProperties: Map[String, Any] = Map(),
                          private val relationshipProperties: Map[String, Any] = Map(),
                          private val limit: Int = 0) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getInstances",
        "args" -> Map(
          "modelName" -> modelName,
          "childrenProps" -> childrenProperties,
          "relProps" -> relationshipProperties,
          "limit" -> limit
        )
      )

      request
    }
  }

  case class getUserFeeds(private val uuid: String,
                          private val limit: Int = 0) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "getUserFeeds",
        "args" -> Map(
          "uuid" -> uuid,
          "limit" -> limit
        )
      )

      request
    }
  }

  case class setLabel(private val uuid: String,
                      private val label: String) extends Method {
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

  case class deleteLabel(private val uuid: String,
                         private val label: String) extends Method {
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

  case class setProperties(private val uuid: String,
                           private val properties: Map[String, Any]) extends Method {
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

  case class deleteProperties(private val uuid: String,
                              private val propertyKeys: List[String]) extends Method {
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

  case class setRelationshipProperties(private val startNodeUuid: String,
                                       private val endNodeUuid: String,
                                       private val properties: Map[String, Any]) extends Method {
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

  case class deleteRelationshipProperties(private val startNodeUuid: String,
                                          private val endNodeUuid: String,
                                          private val propertyKeys: List[String]) extends Method {
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

  case class createNode(private val modelName: String,
                        private val relationshipType: String,
                        private val properties: Map[String, Any]) extends Method {
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

  case class createRelationship(private val startNodeUuid: String,
                                private val endNodeUuid: String,
                                private val relationshipType: String,
                                private val properties: Map[String, Any] = Map()) extends Method {
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

  case class deleteRelationship(private val startNodeUuid: String,
                                private val endNodeUuid: String) extends Method {
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

  case class popRelationship(private val startNodeUuid: String,
                             private val relType: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "popRelationships",
        "args" -> Map(
          "startNodeUuid" -> startNodeUuid,
          "relType" -> relType
        )
      )

      request
    }
  }
}
