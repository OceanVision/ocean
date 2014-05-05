package com.lionfish.correctness

import scala.collection.mutable.ListBuffer
import org.scalatest.{FlatSpec, BeforeAndAfterAll}
import com.lionfish.server.Server
import com.lionfish.client.{Client, Batch}

class Set2 extends FlatSpec with BeforeAndAfterAll {
  private var serverThread: Thread = null
  private val client = new Client
  private var batch: Batch = null

  override def beforeAll() {
    serverThread = new Thread(Server)
    serverThread.start()

    Server.availabilityLock.acquire()
    client.connect()
    Server.availabilityLock.release()
    batch = client.getBatch
  }

  override def afterAll() {
    client.disconnect()
    serverThread.interrupt()
  }

  // =================== SET 2.1 ===================

  "set 2.1" should "accept mixed getModelNodes, getChildren, getInstances, createNode, createRelationship and deleteNode" in {
    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

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

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val children = client.getChildren(modelUuid, relType, childrenProps).run()
      .asInstanceOf[List[Map[String, Any]]]

    val instances = client.getInstances(modelName, childrenProps).run()
      .asInstanceOf[List[Map[String, Any]]]

    client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "-2").run()

    val children2 = client.getChildren(uuidList(0)("uuid"), relType + "-2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(children != null)
    assert(children.length == 1)
    assert(instances != null)
    assert(instances.length == 1)
    assert(children.equals(instances))

    assert(children2 != null)
    assert(children2.length == 1)

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  it should "accept mixed getByUuid, getInstances, createRelationship and deleteNode" in {
    val modelName = "NeoUser"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val instances = client.getInstances(modelName).run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- instances) {
      batch += client.getByUuid(item("uuid").asInstanceOf[String])
    }
    val nodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    assert(instances != null)
    assert(instances.length > 0)

    assert(nodeList != null)
    assert(nodeList.length == instances.length)
    assert(instances.equals(nodeList))

    client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "-2").run()

    val children2 = client.getChildren(uuidList(0)("uuid"), relType + "-2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(children2 != null)
    assert(children2.length == 1)

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  it should "accept mixed getByLink, getInstances and deleteRelationship" in {
    val modelName = "ContentSource"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "link" -> "http://www.example1.com")
    val props1: Map[String, Any] = Map("key0" -> "abc", "link" -> "http://www.example2.com")

    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    var modelUuid: String = null

    for (item <- modelNodeList) {
      if (item("model_name") == modelName) {
        modelUuid = item("uuid")
          .asInstanceOf[String]
      }
    }

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val instances = client.getInstances(modelName).run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- instances) {
      batch += client.getByLink(modelName, item("link").asInstanceOf[String])
    }
    val nodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    client.deleteRelationship(modelUuid, uuidList(0)("uuid")).run()

    val instances2 = client.getInstances(modelName).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(instances != null)
    assert(instances.length > 0)

    assert(nodeList != null)
    assert(nodeList.length == instances.length)
    assert(instances.equals(nodeList))

    assert(instances2 != null)
    assert(instances2.length == instances.length - 1)

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  it should "accept mixed getByUuid, getByLink, getModelNodes, getChildren, deleteNode and deleteRelationship" in {
    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

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

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val children = client.getChildren(modelUuid, relType).run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- children) {
      batch += client.getByUuid(item("uuid").asInstanceOf[String])
    }
    val nodeByUuidList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- children) {
      batch += client.getByLink(modelName, item("link").asInstanceOf[String])
    }
    val nodeByLinkList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    client.deleteRelationship(modelUuid, uuidList(0)("uuid")).run()

    val children2 = client.getChildren(modelUuid, relType).run()
      .asInstanceOf[List[Map[String, Any]]]

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

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  it should "accept mixed getModelNodes, getChildren, createNode and deleteRelationship" in {
    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    val rootUuid = "root"
    val nonExistingUuid = "*abc([)*"
    val relType = "<<TYPE>>"

    client.deleteRelationship(rootUuid, nonExistingUuid).run()

    val children = client.getChildren(rootUuid, relType).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    assert(children != null)
    assert(children.length == modelNodeList.length)

    for (model <- modelNodeList) {
      assert(children.contains(model))
    }
  }

  it should "accept mixed getByUuid, getByLink, getInstances, deleteNode and deleteRelationship" in {
    val modelName = "ContentSource"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "link" -> "http://www.example5.com")
    val props1: Map[String, Any] = Map("key0" -> "abc", "link" -> "http://www.example6.com")

    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    var modelUuid: String = null

    for (item <- modelNodeList) {
      if (item("model_name") == modelName) {
        modelUuid = item("uuid")
          .asInstanceOf[String]
      }
    }

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val instances = client.getInstances(modelName).run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- instances) {
      batch += client.getByUuid(item("uuid").asInstanceOf[String])
    }
    val nodeByUuidList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- instances) {
      batch += client.getByLink(modelName, item("link").asInstanceOf[String])
    }
    val nodeByLinkList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    client.deleteRelationship(modelUuid, uuidList(0)("uuid")).run()

    val instances2 = client.getInstances(modelName).run()
      .asInstanceOf[List[Map[String, Any]]]

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

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  it should "accept mixed getByUuid, getByLink, createNode, createRelationship and deleteRelationship" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_2.1.7>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "link" -> "http://www.example7.com")
    val props1: Map[String, Any] = Map("key0" -> "abc", "link" -> "http://www.example8.com")

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    batch += client.getByUuid(uuidList(0)("uuid"))
    batch += client.getByUuid(uuidList(1)("uuid"))
    val nodeByUuidList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    batch += client.getByLink(modelName, props0("link").asInstanceOf[String])
    batch += client.getByLink(modelName, props1("link").asInstanceOf[String])
    val nodeByLinkList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "-2").run()

    val children = client.getChildren(uuidList(0)("uuid"), relType + "-2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(nodeByUuidList != null)
    assert(nodeByUuidList.length == 2)

    assert(nodeByLinkList != null)
    assert(nodeByLinkList.length == nodeByUuidList.length)
    assert(nodeByUuidList.equals(nodeByLinkList))

    assert(children != null)
    assert(children.length == 1)
    assert(nodeByUuidList(1).equals(children(0)))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }



  // =================== SET 2.2 ===================

  "set 2.2" should "accept mixed getChildren and setProperties" in {
    val modelName = "Content"
    val relType = "<<TEST_2.2.1>>"
    var props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(modelNodeList != null)
    assert(modelNodeList.length > 0)

    var modelUuid: String = null

    for (item <- modelNodeList) {
      if (item("model_name") == modelName) {
        modelUuid = item("uuid")
          .asInstanceOf[String]
      }
    }

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    props0 += "uuid" -> uuidList(0)("uuid")

    val children = client.getChildren(modelUuid, relType).run()
      .asInstanceOf[List[Map[String, Any]]]

    var propsToSet: Map[String, Any] = Map("key1" -> "def", "key2" -> 56)
    client.setProperties(uuidList(0)("uuid"), propsToSet).run()

    val children2 = client.getChildren(modelUuid, relType).run()
      .asInstanceOf[List[Map[String, Any]]]

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

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  it should "accept mixed getByUuid and setProperties" in {
    val modelName = "Content"
    val relType = "<<TEST_2.2.2>>"
    var props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    props0 += "uuid" -> uuidList(0)("uuid")

    val testedNode = client.getByUuid(uuidList(0)("uuid")).run()
      .asInstanceOf[Map[String, Any]]

    var propsToSet: Map[String, Any] = Map("key1" -> "def", "key2" -> 56)
    client.setProperties(uuidList(0)("uuid"), propsToSet).run()

    val testedNode2 = client.getByUuid(uuidList(0)("uuid")).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode2 != null)
    assert(!testedNode.equals(testedNode2))

    propsToSet += "key0" -> props0("key0")
    propsToSet += "uuid" -> uuidList(0)("uuid")

    assert(testedNode.equals(props0))
    assert(testedNode2.equals(propsToSet))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }
}
