package com.lionfish.correctness

import scala.collection.mutable.ListBuffer
import org.scalatest.{FlatSpec, BeforeAndAfterAll}
import com.lionfish.server.Server
import com.lionfish.client.{Client, Batch}

class Set1 extends FlatSpec with BeforeAndAfterAll {
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

  // =================== GET BY UUID ===================

  // not using batch, non-empty output
  "getByUuid" should "return a map" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_GET_BY_UUID>>"
    val props: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    var validNode = props
    validNode += "uuid" -> uuid

    val testedNode = client.getByUuid(uuid).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    client.deleteNode(uuid).run()
  }

  // not using batch, empty output
  it should "return null" in {
    val nonExistingUuid = ""

    val testedNode = client.getByUuid(nonExistingUuid).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode == null)
  }

  // using batch, non-empty output
  it should "return a list of not null maps" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_GET_BY_UUID>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    val validNodeList = ListBuffer(props0, props1)
    validNodeList(0) += "uuid" -> uuid0
    validNodeList(1) += "uuid" -> uuid1

    batch.append(client.getByUuid(uuid0))
    batch.append(client.getByUuid(uuid1))
    val testedNodeList = batch.submit().asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(1) != null)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }

  // using batch, empty output
  it should "return a list of mixed not null and null maps" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_GET_BY_UUID>>"
    val props: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    val nonExistingUuid = ""
    var validNode = props
    validNode += "uuid" -> uuid

    batch.append(client.getByUuid(uuid))
    batch.append(client.getByUuid(nonExistingUuid))
    val testedNodeList = batch.submit().asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(1) == null)
    assert(testedNodeList(0).equals(validNode))

    client.deleteNode(uuid).run()
  }



  // =================== GET BY LINK ===================

  // not using batch, non-empty output
  "getByLink" should "return a map" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_GET_BY_LINK>>"
    val props: Map[String, Any] = Map("key0" -> 1, "link" -> "http://example.com")

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val validNode = client.getByUuid(uuid).run()
      .asInstanceOf[Map[String, Any]]

    val testedNode = client.getByLink(modelName, props("link").asInstanceOf[String]).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    client.deleteNode(uuid).run()
  }

  // not using batch, empty output
  it should "return null" in {
    val nonExistingLink = "*abc([)*"
    val testedNode = client.getByLink("Content", nonExistingLink).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode == null)
  }

  // using batch, non-empty output
  it should "return a list of not null maps" in {
    val modelName = "Content"
    val relType = "<<TEST_GET_BY_LINK>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "link" -> "http://example2.com")
    val props1: Map[String, Any] = Map("key0" -> "abc", "link" -> "http://example3.com")

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    batch.append(client.getByUuid(uuid0))
    batch.append(client.getByUuid(uuid1))
    val validNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    batch.append(client.getByLink("Content", props0("link").asInstanceOf[String]))
    batch.append(client.getByLink("Content", props1("link").asInstanceOf[String]))
    val testedNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(1) != null)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }

  // using batch, empty output
  it should "return a list of mixed not null and null maps" in {
    val modelName = "Content"
    val relType = "<<TEST_GET_BY_LINK>>"
    val props: Map[String, Any] = Map("key0" -> 1, "link" -> "http://example4.com")

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val nonExistingLink = "*abc([)*"

    val validNode = client.getByUuid(uuid).run()
      .asInstanceOf[Map[String, Any]]

    batch.append(client.getByLink("Content", props("link").asInstanceOf[String]))
    batch.append(client.getByLink("Content", nonExistingLink))
    val testedNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList(0) != null)
    assert(testedNodeList(1) == null)
    assert(testedNodeList(0).equals(validNode))

    client.deleteNode(uuid).run()
  }



  // =================== GET MODEL NODES ===================

  // not using batch, non-empty output
  "getModelNodes" should "return a list of maps" in {
    val testedNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)

    for (item <- testedNodeList) {
      assert(item.contains("uuid"))
      batch.append(client.getByUuid(item("uuid").asInstanceOf[String]))
    }
    val validNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList.equals(validNodeList))
  }

  // not using batch, empty output
  it should "return null" in {

  }

  // using batch, non-empty output
  it should "return a list of not null lists of maps" in {
    batch.append(client.getModelNodes())
    batch.append(client.getModelNodes())

    val testedNodeList = batch.submit()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)

    for (item <- testedNodeList(0)) {
      assert(item.contains("uuid"))
      batch.append(client.getByUuid(item("uuid").asInstanceOf[String]))
    }
    val validNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- testedNodeList) {
      assert(item.equals(validNodeList))
    }
  }

  // using batch, empty output
  it should "return a list of mixed not null and null lists of maps" in {

  }



  // =================== GET CHILDREN ===================

  // not using batch, non-empty output, empty props
  "getChildren" should "return a list of maps" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_GET_CHILDREN>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    var modelUuid = ""

    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    batch.append(client.getByUuid(uuid0))
    batch.append(client.getByUuid(uuid1))
    val validNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList = client.getChildren(modelUuid, relType).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)

    val foundList = ListBuffer(0, 0)
    for (item <- testedNodeList) {
      if (item.equals(validNodeList(0))) {
        foundList(0) += 1
      } else if (item.equals(validNodeList(1))) {
        foundList(1) += 1
      }
    }

    assert(foundList(0) == 1)
    assert(foundList(1) == 1)

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }

  // not using batch, empty output, non-empty props
  it should "return an empty list" in {
    val nonExistingUuid = "*abc([)*"
    val relType = "<<TEST_GET_CHILDREN>>"
    val childrenProps: Map[String, Any] = Map("key0" -> 1)

    val testedNodeList = client.getChildren(nonExistingUuid, relType, childrenProps).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)
  }

  // using batch, non-empty output, non-empty props
  it should "return a list of lists of not null maps" in {
    val modelName = "Content"
    val relType = "<<TEST_GET_CHILDREN>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val childrenProps0: Map[String, Any] = Map("key0" -> 1)
    val childrenProps1: Map[String, Any] = Map("key0" -> "abc")
    var modelUuid = ""

    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    batch.append(client.getByUuid(uuid0))
    batch.append(client.getByUuid(uuid1))
    val validNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    batch.append(client.getChildren(modelUuid, relType, childrenProps0))
    batch.append(client.getChildren(modelUuid, relType, childrenProps1))
    val testedNodeList = batch.submit()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length == 1)
    assert(testedNodeList(1) != null)
    assert(testedNodeList(1).length == 1)
    assert(testedNodeList(0)(0).equals(validNodeList(0)))
    assert(testedNodeList(1)(0).equals(validNodeList(1)))

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }

  // using batch, empty output, empty props
  it should "return a list of mixed non-empty and empty lists of maps" in {
    val modelName = "Content"
    val relType = "<<TEST_GET_CHILDREN>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    var modelUuid = ""
    val nonExistingUuid = "*abc([)*"

    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    batch.append(client.getByUuid(uuid0))
    batch.append(client.getByUuid(uuid1))
    val validNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    batch.append(client.getChildren(nonExistingUuid, relType))
    batch.append(client.getChildren(modelUuid, relType))
    val testedNodeList = batch.submit()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length == 0)
    assert(testedNodeList(1) != null)
    assert(testedNodeList(1).length == 2)

    val foundList = ListBuffer(0, 0)
    for (item <- testedNodeList(1)) {
      if (item.equals(validNodeList(0))) {
        foundList(0) += 1
      } else if (item.equals(validNodeList(1))) {
        foundList(1) += 1
      }
    }

    assert(foundList(0) == 1)
    assert(foundList(1) == 1)

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }



  // =================== GET INSTANCES ===================

  // not using batch, non-empty output, empty props
  "getInstances" should "return a list of maps" in {
    val modelName = "NeoUser"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    batch.append(client.getByUuid(uuid0))
    batch.append(client.getByUuid(uuid1))
    val validNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList = client.getInstances(modelName).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length >= 2)

    val foundList = ListBuffer(0, 0)
    for (item <- testedNodeList) {
      if (item.equals(validNodeList(0))) {
        foundList(0) += 1
      } else if (item.equals(validNodeList(1))) {
        foundList(1) += 1
      }
    }

    assert(foundList(0) == 1)
    assert(foundList(1) == 1)

    batch.append(client.deleteNode(uuid0))
    batch.append(client.deleteNode(uuid1))
    batch.submit()
  }

  // not using batch, empty output, non-empty props
  it should "return an empty list" in {
    val nonExistingModelName = "*abc([)*"
    val childrenProps: Map[String, Any] = Map("key0" -> 1)

    val testedNodeList = client.getInstances(nonExistingModelName, childrenProps).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)
  }

  // using batch, non-empty output, non-empty props
  it should "return a list of lists of not null maps" in {
    val modelName = "Content"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val childrenProps0: Map[String, Any] = Map("key0" -> 1)
    val childrenProps1: Map[String, Any] = Map("key0" -> "abc")

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    batch.append(client.getByUuid(uuid0))
    batch.append(client.getByUuid(uuid1))
    val validNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    batch.append(client.getInstances(modelName, childrenProps0))
    batch.append(client.getInstances(modelName, childrenProps1))
    val testedNodeList = batch.submit()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length >= 1)
    assert(testedNodeList(1) != null)
    assert(testedNodeList(1).length >= 1)

    val foundList = ListBuffer(0, 0)
    for (item <- testedNodeList(0)) {
      if (item.equals(validNodeList(0))) {
        foundList(0) += 1
      }
    }

    for (item <- testedNodeList(1)) {
      if (item.equals(validNodeList(1))) {
        foundList(1) += 1
      }
    }

    assert(foundList(0) == 1)
    assert(foundList(1) == 1)

    batch.append(client.deleteNode(uuid0))
    batch.append(client.deleteNode(uuid1))
    batch.submit()
  }

  // using batch, empty output, empty props
  it should "return a list of mixed non-empty and empty lists of maps" in {
    val modelName = "Content"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingModelName = "*abc([)*"

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    batch.append(client.getByUuid(uuid0))
    batch.append(client.getByUuid(uuid1))
    val validNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    batch.append(client.getInstances(nonExistingModelName))
    batch.append(client.getInstances(modelName))
    val testedNodeList = batch.submit()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length == 0)
    assert(testedNodeList(1) != null)
    assert(testedNodeList(1).length >= 2)

    val foundList = ListBuffer(0, 0)
    for (item <- testedNodeList(1)) {
      if (item.equals(validNodeList(0))) {
        foundList(0) += 1
      } else if (item.equals(validNodeList(1))) {
        foundList(1) += 1
      }
    }

    assert(foundList(0) == 1)
    assert(foundList(1) == 1)

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }



  // =================== SET PROPERTIES ===================

  // not using batch, correct input
  "setProperties" should "set properties to a node" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_SET_PROPERTIES>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet: Map[String, Any] = Map("key1" -> 55, "key2" -> 32)

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    client.setProperties(uuid, propsToSet).run()

    val validNode: Map[String, Any] = Map("uuid" -> uuid, "key0" -> "abc", "key1" -> 55, "key2" -> 32)

    val testedNode = client.getByUuid(uuid).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    client.deleteNode(uuid).run()
  }

  // not using batch, incorrect input
  it should "not set properties to a node" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_SET_PROPERTIES>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet: Map[String, Any] = null

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    var validNode = props
    validNode += "uuid" -> uuid

    client.setProperties(uuid, propsToSet).run()

    val testedNode = client.getByUuid(uuid).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    client.deleteNode(uuid).run()
  }

  // using batch, correct input
  it should "set properties to exactly two nodes" in {
    val modelName = "Content"
    val relType = "<<TEST_SET_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet0: Map[String, Any] = Map("key1" -> 55, "key2" -> 12)
    val propsToSet1: Map[String, Any] = Map("key1" -> 0, "key2" -> "")

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    val validNodeList = List(
      Map("uuid" -> uuid0, "key0" -> 1, "key1" -> 55, "key2" -> 12),
      Map("uuid" -> uuid1, "key0" -> "abc", "key1" -> 0, "key2" -> "")
    )

    batch += client.setProperties(uuid0, propsToSet0)
    batch += client.setProperties(uuid1, propsToSet1)
    batch.submit()

    batch += client.getByUuid(uuid0)
    batch += client.getByUuid(uuid1)
    val testedNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }

  // using batch, incorrect input
  it should "set properties only to one node" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_SET_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet0: Map[String, Any] = null
    val propsToSet1: Map[String, Any] = Map("key1" -> 0, "key2" -> "")

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    val validNodeList = List(
      Map("uuid" -> uuid0, "key0" -> 1, "key1" -> "string"),
      Map("uuid" -> uuid1, "key0" -> "abc", "key1" -> 0, "key2" -> "")
    )

    batch += client.setProperties(uuid0, propsToSet0)
    batch += client.setProperties(uuid1, propsToSet1)
    batch.submit()

    batch += client.getByUuid(uuid0)
    batch += client.getByUuid(uuid1)
    val testedNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }



  // =================== DELETE PROPERTIES ===================

  // not using batch, correct input
  "deleteProperties" should "delete node's properties" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_DELETE_PROPERTIES>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToDelete: List[String] = List("key1")

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    client.deleteProperties(uuid, propsToDelete).run()

    val validNode: Map[String, Any] = Map("uuid" -> uuid, "key0" -> "abc")

    val testedNode = client.getByUuid(uuid).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    client.deleteNode(uuid).run()
  }

  // not using batch, incorrect input
  it should "not delete node's properties" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_DELETE_PROPERTIES>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToDelete: List[String] = List("nonExistingKey")

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    var validNode = props
    validNode += "uuid" -> uuid

    client.deleteProperties(uuid, propsToDelete).run()

    val testedNode = client.getByUuid(uuid).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    client.deleteNode(uuid).run()
  }

  // using batch, correct input
  it should "delete properties of exactly two nodes" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToDelete0: List[String] = List("key0")
    val propsToDelete1: List[String] = List("key1")

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    val validNodeList = List(
      Map("uuid" -> uuid0, "key1" -> "string"),
      Map("uuid" -> uuid1, "key0" -> "abc")
    )

    batch += client.deleteProperties(uuid0, propsToDelete0)
    batch += client.deleteProperties(uuid1, propsToDelete1)
    batch.submit()

    batch += client.getByUuid(uuid0)
    batch += client.getByUuid(uuid1)
    val testedNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }

  // using batch, incorrect input
  it should "delete properties of only one node" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_DELETE_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToDelete0: List[String] = List("nonExistingKey")
    val propsToDelete1: List[String] = List("key1")

    val uuid0 = client.createNode(modelName, relType, props0).run()
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = client.createNode(modelName, relType, props1).run()
      .asInstanceOf[Map[String, String]]("uuid")

    val validNodeList = List(
      Map("uuid" -> uuid0, "key0" -> 1, "key1" -> "string"),
      Map("uuid" -> uuid1, "key0" -> "abc")
    )

    batch += client.deleteProperties(uuid0, propsToDelete0)
    batch += client.deleteProperties(uuid1, propsToDelete1)
    batch.submit()

    batch += client.getByUuid(uuid0)
    batch += client.getByUuid(uuid1)
    val testedNodeList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    client.deleteNode(uuid0).run()
    client.deleteNode(uuid1).run()
  }



  // =================== CREATE NODE ===================

  // not using batch, correct input
  "createNode" should "create a node with properties" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_NODE>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    var validNode = props
    validNode += "uuid" -> uuid

    val testedNode = client.getByUuid(uuid).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    client.deleteNode(uuid).run()
  }

  // not using batch, incorrect input
  it should "not create any node" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_NODE>>"
    val props: Map[String, Any] = Map()

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    assert(uuid == null)
  }

  // using batch, correct input
  it should "create exactly two nodes with properties" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_NODE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    var modelUuid = ""

    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    assert(uuidList != null)
    assert(uuidList.length == 2)

    val validNodeList = ListBuffer(props0, props1)
    validNodeList(0) += "uuid" -> uuidList(0)("uuid")
    validNodeList(1) += "uuid" -> uuidList(1)("uuid")

    val testedNodeList = client.getChildren(modelUuid, relType).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)

    val foundList = ListBuffer(0, 0)
    for (item <- testedNodeList) {
      if (item.equals(validNodeList(0))) {
        foundList(0) += 1
      } else if (item.equals(validNodeList(1))) {
        foundList(1) += 1
      }
    }

    assert(foundList(0) == 1)
    assert(foundList(1) == 1)

    client.deleteNode(uuidList(0)("uuid")).run()
    client.deleteNode(uuidList(1)("uuid")).run()
  }

  // using batch, incorrect input
  it should "create only one node with properties" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_CREATE_NODE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = null

    var modelUuid = ""

    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, Any]]]

    assert(uuidList != null)
    assert(uuidList.length == 2)
    assert(uuidList(0) != null)
    assert(uuidList(1) != null)
    assert(uuidList(0)("uuid") != null)
    assert(uuidList(1)("uuid") == null)

    var validNode = props0
    validNode += "uuid" -> uuidList(0)("uuid")

    val testedNodeList = client.getChildren(modelUuid, relType).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)

    var found = 0
    for (item <- testedNodeList) {
      if (item.equals(validNode)) {
        found += 1
      }
    }

    assert(found == 1)

    client.deleteNode(uuidList(0)("uuid").asInstanceOf[String]).run()
    client.deleteNode(uuidList(1)("uuid").asInstanceOf[String]).run()
  }



  // =================== DELETE NODE ===================

  // not using batch, correct input
  "deleteNode" should "delete a node" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_NODE>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    client.deleteNode(uuid).run()

    val testedNode = client.getByUuid(uuid).run()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode == null)
  }

  // not using batch, incorrect input
  it should "not delete any node" in {

  }

  // using batch, correct input
  it should "delete exactly two nodes" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_NODE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    var modelUuid = ""

    val modelNodeList = client.getModelNodes().run()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()

    val validNodeList = ListBuffer(props0, props1)
    validNodeList(0) += "uuid" -> uuidList(0)("uuid")
    validNodeList(1) += "uuid" -> uuidList(1)("uuid")

    val testedNodeList = client.getChildren(modelUuid, relType).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)
  }

  // using batch, incorrect input
  it should "delete only one node" in {

  }



  // =================== CREATE RELATIONSHIP ===================

  // not using batch, correct input, empty props
  "createRelationship" should "create a relationship without properties" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_RELATIONSHIP>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2").run()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNode))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  // not using batch, incorrect input, non-empty props
  it should "not create any relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_RELATIONSHIP>>"
    val props: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")

    val nonExistingUuid = "*abc([)*"
    val relProps: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")

    val uuid = client.createNode(modelName, relType, props).run()
      .asInstanceOf[Map[String, String]]("uuid")

    client.createRelationship(uuid, nonExistingUuid, relType + "2", relProps).run()

    val testedNodeList = client.getChildren(uuid, relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)

    client.deleteNode(uuid).run()
  }

  // using batch, correct input, non-empty props
  it should "create exactly two relationships with properties" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_RELATIONSHIP>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relProps0: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val relProps1: Map[String, Any] = Map("keyA" -> "aba", "keyB" -> "aab")

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    batch += client.createNode(modelName, relType, props2)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps0)
    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2", relProps1)
    batch.submit()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)

    val foundList = ListBuffer(0, 0)
    for (item <- testedNodeList) {
      if (item.equals(validNodeList(0))) {
        foundList(0) += 1
      } else if (item.equals(validNodeList(1))) {
        foundList(1) += 1
      }
    }

    assert(foundList(0) == 1)
    assert(foundList(1) == 1)

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch += client.deleteNode(uuidList(2)("uuid"))
    batch.submit()
  }

  // using batch, incorrect input, empty props
  it should "create only one relationship without properties" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_RELATIONSHIP>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingUuid = "*abc([)*"

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batch += client.createRelationship(uuidList(0)("uuid"), nonExistingUuid, relType + "2")
    batch.submit()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNode))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }



  // =================== DELETE RELATIONSHIP ===================

  // not using batch, correct input
  "deleteRelationship" should "delete a relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2").run()
    client.deleteRelationship(uuidList(0)("uuid"), uuidList(1)("uuid")).run()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  // not using batch, incorrect input
  it should "not delete any relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingUuid = "*abc([)*"

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2").run()
    client.deleteRelationship(uuidList(0)("uuid"), nonExistingUuid).run()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNode))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  // using batch, correct input
  it should "delete exactly two relationships" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    batch += client.createNode(modelName, relType, props2)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2")
    batch.submit()

    batch += client.deleteRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"))
    batch += client.deleteRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"))
    batch.submit()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch += client.deleteNode(uuidList(2)("uuid"))
    batch.submit()
  }

  // using batch, incorrect input
  it should "delete only one relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val nonExistingUuid = "*abc([)*"

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    batch += client.createNode(modelName, relType, props2)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2")
    batch.submit()

    batch += client.deleteRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"))
    batch += client.deleteRelationship(uuidList(0)("uuid"), nonExistingUuid)
    batch.submit()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNodeList(1)))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch += client.deleteNode(uuidList(2)("uuid"))
    batch.submit()
  }



  // =================== SET RELATIONSHIP PROPERTIES ===================

  // not using batch, correct input
  "setRelationshipProperties" should "set properties to a relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_SET_RELATIONSHIP_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet: Map[String, Any] = Map("relKey" -> 92)

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2").run()
    client.setRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), propsToSet).run()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList2 = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), propsToSet).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNode))

    assert(testedNodeList.equals(testedNodeList2))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  // not using batch, incorrect input
  it should "not set properties to a relationship" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_SET_RELATIONSHIP_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingUuid = "*abc([)*"
    val relProps: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val propsToSet: Map[String, Any] = Map("relKey" -> 92)

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    client.createRelationship(uuidList(0)("uuid"), nonExistingUuid, relType + "2", relProps).run()
    client.setRelationshipProperties(uuidList(0)("uuid"), nonExistingUuid, propsToSet).run()
    client.setRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), null).run()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2", propsToSet).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  // using batch, correct input
  it should "set properties to exactly two relationships" in {
    val modelName = "Content"
    val relType = "<<TEST_SET_RELATIONSHIP_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relPropsToSet0: Map[String, Any] = Map("relKey" -> 92)
    val relPropsToSet1: Map[String, Any] = Map("relKey" -> 78)

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    batch += client.createNode(modelName, relType, props2)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2")
    batch.submit()

    batch += client.setRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), relPropsToSet0)
    batch += client.setRelationshipProperties(uuidList(0)("uuid"), uuidList(2)("uuid"), relPropsToSet1)
    batch.submit()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relPropsToSet0).run()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList2 = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relPropsToSet1).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNodeList(0)))

    assert(testedNodeList2 != null)
    assert(testedNodeList2.length == 1)
    assert(testedNodeList2(0).equals(validNodeList(1)))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch += client.deleteNode(uuidList(2)("uuid"))
    batch.submit()
  }

  // using batch, incorrect input
  it should "set properties only to one relationship" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_SET_RELATIONSHIP_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relPropsToSet0: Map[String, Any] = Map("relKey" -> 92)
    val relPropsToSet1: Map[String, Any] = null

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    batch += client.createNode(modelName, relType, props2)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2")
    batch.submit()

    batch += client.setRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), relPropsToSet0)
    batch += client.setRelationshipProperties(uuidList(0)("uuid"), uuidList(2)("uuid"), relPropsToSet1)
    batch.submit()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relPropsToSet0).run()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList2 = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relPropsToSet1).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNodeList(0)))

    assert(testedNodeList2 != null)
    assert(testedNodeList2.length == 2)

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch += client.deleteNode(uuidList(2)("uuid"))
    batch.submit()
  }



  // =================== DELETE RELATIONSHIP PROPERTIES ===================

  // not using batch, correct input
  "deleteRelationshipProperties" should "delete relationship's properties" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val relProps: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val propsToDelete: List[String] = List("keyB")

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps).run()
    client.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), propsToDelete).run()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2").run()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList2 = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relProps).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNode))

    assert(testedNodeList2 != null)
    assert(testedNodeList2.length == 0)

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  // not using batch, incorrect input
  it should "not delete relationship's properties" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_DELETE_RELATIONSHIP_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingUuid = "*abc([)*"
    val relProps: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val propsToDelete: List[String] = List("keyB")

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps).run()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relProps).run()
      .asInstanceOf[List[Map[String, Any]]]

    client.deleteRelationshipProperties(uuidList(0)("uuid"), nonExistingUuid, propsToDelete).run()
    client.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), null).run()

    val testedNodeList2 = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relProps).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)

    assert(testedNodeList2 != null)
    assert(testedNodeList2.length == 1)
    assert(testedNodeList.equals(testedNodeList2))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch.submit()
  }

  // using batch, correct input
  it should "delete properties of exactly two relationships" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relProps0: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val relProps1: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "bca")

    val relPropsToDelete0: List[String] = List("keyA")
    val relPropsToDelete1: List[String] = List("keyB")

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    batch += client.createNode(modelName, relType, props2)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    val validProps0: Map[String, Any] = Map("keyB" -> "aaa")
    val validProps1: Map[String, Any] = Map("keyA" -> 5)

    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps0)
    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2", relProps1)
    batch.submit()

    batch += client.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), relPropsToDelete0)
    batch += client.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(2)("uuid"), relPropsToDelete1)
    batch.submit()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), validProps0).run()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList2 = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), validProps1).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNodeList(0)))

    assert(testedNodeList2 != null)
    assert(testedNodeList2.length == 1)
    assert(testedNodeList2(0).equals(validNodeList(1)))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch += client.deleteNode(uuidList(2)("uuid"))
    batch.submit()
  }

  // using batch, incorrect input
  it should "delete properties of only one relationship" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_DELETE_RELATIONSHIP_PROPERTIES>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relProps0: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val relProps1: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "bca")

    val relPropsToDelete0: List[String] = null
    val relPropsToDelete1: List[String] = List("keyB")

    batch += client.createNode(modelName, relType, props0)
    batch += client.createNode(modelName, relType, props1)
    batch += client.createNode(modelName, relType, props2)
    val uuidList = batch.submit()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    val validProps1: Map[String, Any] = Map("keyA" -> 5)

    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps0)
    batch += client.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2", relProps1)
    batch.submit()

    val testedNodeList = client.getChildren(uuidList(0)("uuid"), relType + "2", Map()).run()
      .asInstanceOf[List[Map[String, Any]]]

    batch += client.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), relPropsToDelete0)
    batch += client.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(2)("uuid"), relPropsToDelete1)
    batch.submit()

    val testedNodeList2 = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relProps0).run()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList3 = client.getChildren(uuidList(0)("uuid"), relType + "2", Map(), validProps1).run()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList2 != null)
    assert(testedNodeList2.length == 1)
    assert(testedNodeList2(0).equals(validNodeList(0)))

    assert(testedNodeList3 != null)
    assert(testedNodeList3.length == 2)
    assert(testedNodeList.equals(testedNodeList3))

    batch += client.deleteNode(uuidList(0)("uuid"))
    batch += client.deleteNode(uuidList(1)("uuid"))
    batch += client.deleteNode(uuidList(2)("uuid"))
    batch.submit()
  }
}
