package com.lionfish.correctness

import org.scalatest.{FlatSpec, BeforeAndAfterAll}
import com.lionfish.server.{Server, Launcher}
import com.lionfish.client._
import com.lionfish.utils.Config

class Set2 extends FlatSpec with BeforeAndAfterAll {
  private var seqStream: Stream = null
  private var batchStream: Stream = null

  override def beforeAll() {
    val address = Config.debugServerAddress
    val port = Config.debugServerPort
    Launcher.main(Array("--debug"))
    Database.setServerAddress(address)
    Database.setServerPort(port)
  }

  // =================== SET 2.1 ===================

  "set 2.1" should "accept mixed getModelNodes, getChildren, getInstances, createNode, createRelationship and deleteNode" in {
    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream

    val modelNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    val modelName = modelNodeList(0)("model_name")
      .asInstanceOf[String]
    val modelUuid = modelNodeList(0)("uuid")
      .asInstanceOf[String]
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val childrenProps: Map[String, Any] = Map("key0" -> "abc")

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val children = (seqStream !! Database.getChildren(modelUuid, relType, childrenProps))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    val instances = (seqStream !! Database.getInstances(modelName, childrenProps))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "-2")

    val children2 = (seqStream !! Database.getChildren(uuidList(0)("uuid"), relType + "-2"))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(children != null)
    assert(children.length == 1)
    assert(instances != null)
    assert(instances.length == 1)
    assert(children.equals(instances))

    assert(children2 != null)
    assert(children2.length == 1)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()

    seqStream.close()
    batchStream.close()
  }

  it should "accept mixed getByUuid, getInstances, createRelationship and deleteNode" in {
    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream

    val modelName = "NeoUser"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val instances = (seqStream !! Database.getInstances(modelName))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    for (item <- instances) {
      batchStream << Database.getByUuid(item("uuid").asInstanceOf[String])
    }
    val nodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(instances != null)
    assert(instances.length > 0)

    assert(nodeList != null)
    assert(nodeList.length == instances.length)
    assert(instances.equals(nodeList))

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "-2")

    val children2 = (seqStream !! Database.getChildren(uuidList(0)("uuid"), relType + "-2"))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(children2 != null)
    assert(children2.length == 1)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()

    seqStream.close()
    batchStream.close()
  }

  it should "accept mixed getByLink, getInstances and deleteRelationship" in {
    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream

    val modelName = "ContentSource"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "link" -> "http://www.example1.com")
    val props1: Map[String, Any] = Map("key0" -> "abc", "link" -> "http://www.example2.com")

    val modelNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    var modelUuid: String = null

    for (item <- modelNodeList) {
      if (item("model_name") == modelName) {
        modelUuid = item("uuid")
          .asInstanceOf[String]
      }
    }

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val instances = (seqStream !! Database.getInstances(modelName))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    for (item <- instances) {
      batchStream << Database.getByLink(modelName, item("link").asInstanceOf[String])
    }
    val nodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    seqStream !! Database.deleteRelationship(modelUuid, uuidList(0)("uuid"))

    val instances2 = (seqStream !! Database.getInstances(modelName))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(instances != null)
    assert(instances.length > 0)

    assert(nodeList != null)
    assert(nodeList.length == instances.length)
    assert(instances.equals(nodeList))

    assert(instances2 != null)
    assert(instances2.length == instances.length - 1)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()

    seqStream.close()
    batchStream.close()
  }

  it should "accept mixed getByUuid, getByLink, getModelNodes, getChildren, deleteNode and deleteRelationship" in {
    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream

    val modelNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    var modelName: String = null
    var modelUuid: String = null

    for (item <- modelNodeList) {
      if (item("model_name") == "ContentSource") {
        modelName = item("model_name")
          .asInstanceOf[String]
        modelUuid = item("uuid")
          .asInstanceOf[String]
      }
    }

    val relType = "<<TEST_2.1.4>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "link" -> "http://www.example3.com")
    val props1: Map[String, Any] = Map("key0" -> "abc", "link" -> "http://www.example4.com")

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val children = (seqStream !! Database.getChildren(modelUuid, relType))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    for (item <- children) {
      batchStream << Database.getByUuid(item("uuid").asInstanceOf[String])
    }
    val nodeByUuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- children) {
      batchStream << Database.getByLink(modelName, item("link").asInstanceOf[String])
    }
    val nodeByLinkList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    seqStream !! Database.deleteRelationship(modelUuid, uuidList(0)("uuid"))

    val children2 = (seqStream !! Database.getChildren(modelUuid, relType))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(children != null)
    assert(children.length > 0)

    assert(nodeByUuidList != null)
    assert(nodeByUuidList.length == children.length)
    assert(children.equals(nodeByUuidList))

    assert(nodeByLinkList != null)
    assert(nodeByLinkList.length == nodeByUuidList.length)
    assert(nodeByUuidList.equals(nodeByLinkList))

    assert(children2 != null)
    assert(children2.length == children.length - 1)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()

    seqStream.close()
    batchStream.close()
  }

  it should "accept mixed getModelNodes, getChildren, createNode and deleteRelationship" in {
    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream

    val modelNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    val rootUuid = "root"
    val nonExistingUuid = "*abc([)*"
    val relType = "<<TYPE>>"

    seqStream !! Database.deleteRelationship(rootUuid, nonExistingUuid)

    val children = (seqStream !! Database.getChildren(rootUuid, relType))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    assert(children != null)
    assert(children.length == modelNodeList.length)

    for (model <- modelNodeList) {
      assert(children.contains(model))
    }

    seqStream.close()
    batchStream.close()
  }

  it should "accept mixed getByUuid, getByLink, getInstances, deleteNode and deleteRelationship" in {
    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream

    val modelName = "ContentSource"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "link" -> "http://www.example5.com")
    val props1: Map[String, Any] = Map("key0" -> "abc", "link" -> "http://www.example6.com")

    val modelNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    var modelUuid: String = null

    for (item <- modelNodeList) {
      if (item("model_name") == modelName) {
        modelUuid = item("uuid")
          .asInstanceOf[String]
      }
    }

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val instances = (seqStream !! Database.getInstances(modelName))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    for (item <- instances) {
      batchStream << Database.getByUuid(item("uuid").asInstanceOf[String])
    }
    val nodeByUuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- instances) {
      batchStream << Database.getByLink(modelName, item("link").asInstanceOf[String])
    }
    val nodeByLinkList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    seqStream !! Database.deleteRelationship(modelUuid, uuidList(0)("uuid"))

    val instances2 = (seqStream !! Database.getInstances(modelName))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(instances != null)
    assert(instances.length > 0)

    assert(nodeByUuidList != null)
    assert(nodeByUuidList.length == instances.length)
    assert(instances.equals(nodeByUuidList))

    assert(nodeByLinkList != null)
    assert(nodeByLinkList.length == nodeByUuidList.length)
    assert(nodeByUuidList.equals(nodeByLinkList))

    assert(instances2 != null)
    assert(instances2.length == instances.length - 1)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()

    seqStream.close()
    batchStream.close()
  }

  it should "accept mixed getByUuid, getByLink, createNode, createRelationship and deleteRelationship" in {
    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream

    val modelName = "ContentSource"
    val relType = "<<TEST_2.1.7>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "link" -> "http://www.example7.com")
    val props1: Map[String, Any] = Map("key0" -> "abc", "link" -> "http://www.example8.com")

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    batchStream << Database.getByUuid(uuidList(0)("uuid"))
    batchStream << Database.getByUuid(uuidList(1)("uuid"))
    val nodeByUuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    batchStream << Database.getByLink(modelName, props0("link").asInstanceOf[String])
    batchStream << Database.getByLink(modelName, props1("link").asInstanceOf[String])
    val nodeByLinkList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "-2")

    val children = (seqStream !! Database.getChildren(uuidList(0)("uuid"), relType + "-2"))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(nodeByUuidList != null)
    assert(nodeByUuidList.length == 2)

    assert(nodeByLinkList != null)
    assert(nodeByLinkList.length == nodeByUuidList.length)
    assert(nodeByUuidList.equals(nodeByLinkList))

    assert(children != null)
    assert(children.length == 1)
    assert(nodeByUuidList(1).equals(children(0)))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()

    seqStream.close()
    batchStream.close()
  }



  // =================== SET 2.2 ===================

  "set 2.2" should "accept mixed getChildren and setProperties" in {
    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream

    val modelName = "Content"
    val relType = "<<TEST_2.2.1>>"
    var props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val modelNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    var modelUuid: String = null

    for (item <- modelNodeList) {
      if (item("model_name") == modelName) {
        modelUuid = item("uuid")
          .asInstanceOf[String]
      }
    }

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    props0 += "uuid" -> uuidList(0)("uuid")

    val children = (seqStream !! Database.getChildren(modelUuid, relType))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    var propsToSet: Map[String, Any] = Map("key1" -> "def", "key2" -> 56)
    seqStream !! Database.setProperties(uuidList(0)("uuid"), propsToSet)

    val children2 = (seqStream !! Database.getChildren(modelUuid, relType))
      .asInstanceOf[List[List[Map[String, Any]]]](0)

    assert(children != null)
    assert(children.length == 2)

    assert(children2 != null)
    assert(children2.length == children.length)
    assert(!children.equals(children2))

    var found: Map[String, Any] = null
    var found2: Map[String, Any] = null

    for (item <- children) {
      if (item("uuid").asInstanceOf[String] == uuidList(0)("uuid")) {
        found = item
      }
    }

    for (item <- children2) {
      if (item("uuid").asInstanceOf[String] == uuidList(0)("uuid")) {
        found2 = item
      }
    }

    propsToSet += "key0" -> props0("key0")
    propsToSet += "uuid" -> uuidList(0)("uuid")

    assert(found != null)
    assert(found.equals(props0))
    assert(found2 != null)
    assert(found2.equals(propsToSet))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()

    seqStream.close()
    batchStream.close()
  }

  it should "accept mixed getByUuid and setProperties" in {
    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream

    val modelName = "Content"
    val relType = "<<TEST_2.2.2>>"
    var props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    props0 += "uuid" -> uuidList(0)("uuid")

    val testedNode = (seqStream !! Database.getByUuid(uuidList(0)("uuid")))
      .asInstanceOf[List[Map[String, Any]]](0)

    var propsToSet: Map[String, Any] = Map("key1" -> "def", "key2" -> 56)
    seqStream !! Database.setProperties(uuidList(0)("uuid"), propsToSet)

    val testedNode2 = (seqStream !! Database.getByUuid(uuidList(0)("uuid")))
      .asInstanceOf[List[Map[String, Any]]](0)

    assert(testedNode != null)
    assert(testedNode2 != null)
    assert(!testedNode.equals(testedNode2))

    propsToSet += "key0" -> props0("key0")
    propsToSet += "uuid" -> uuidList(0)("uuid")

    assert(testedNode.equals(props0))
    assert(testedNode2.equals(propsToSet))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()

    seqStream.close()
    batchStream.close()
  }
}
