package com.lionfish.client

object Database extends Factory {
  def getBatchStream: Stream = {
    new BatchStream
  }

  def getSequenceStream: Stream = {
    new SequenceStream
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

  case class deleteNode(private val nodeUuid: String) extends Method {
    override def getRequest: Map[String, Any] = {
      val request = Map(
        "methodName" -> "deleteNodes",
        "args" -> Map(
          "uuid" -> nodeUuid
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
