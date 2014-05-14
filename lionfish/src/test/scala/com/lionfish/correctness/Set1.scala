package com.lionfish.correctness

import scala.collection.mutable.ListBuffer
import org.scalatest.{FlatSpec, BeforeAndAfterAll}
import com.lionfish.server.Launcher
import com.lionfish.client._
import com.lionfish.utils.Config

class Set1 extends FlatSpec with BeforeAndAfterAll {
  private var seqStream: Stream = null
  private var batchStream: Stream = null

  override def beforeAll() {
    val address = Config.debugProxyAddress
    val port = Config.debugProxyPort
    Launcher.main(Array("--debug"))
    Database.setProxyAddress(address)
    Database.setProxyPort(port)

    seqStream = Database.getSequenceStream
    batchStream = Database.getBatchStream
  }

  // =================== GET BY UUID ===================

  // not using batch, non-empty output
  "getByUuid" should "return a map" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_GET_BY_UUID-1>>"
    val props: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")

    val uuid = (seqStream !! Database.createNode(modelName, relType, props))
      .asInstanceOf[Map[String, String]]("uuid")

    var validNode = props
    validNode += "uuid" -> uuid

    val testedNode = (seqStream !! Database.getByUuid(uuid))
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    seqStream !! Database.deleteNode(uuid)
  }

  // not using batch, empty output
  it should "return null" in {
    val nonExistingUuid = ""

    val testedNode = (seqStream !! Database.getByUuid(nonExistingUuid))
      .asInstanceOf[Map[String, Any]]

    assert(testedNode == null)
  }

  // using batch, non-empty output
  it should "return a list of not null maps" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_GET_BY_UUID-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    seqStream << Database.createNode(modelName, relType, props0)
    seqStream << Database.createNode(modelName, relType, props1)
    val uuidList = seqStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props0, props1)
    validNodeList(0) += "uuid" -> uuidList(0)("uuid")
    validNodeList(1) += "uuid" -> uuidList(1)("uuid")

    batchStream << Database.getByUuid(uuidList(0)("uuid"))
    batchStream << Database.getByUuid(uuidList(1)("uuid"))
    val testedNodeList = batchStream.execute().asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(1) != null)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    seqStream !! Database.deleteNode(uuidList(0)("uuid"))
    seqStream !! Database.deleteNode(uuidList(1)("uuid"))
  }

  // using batch, empty output
  it should "return a list of mixed not null and null maps" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_GET_BY_UUID-4>>"
    val props: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")

    val uuid = (seqStream !! Database.createNode(modelName, relType, props))
      .asInstanceOf[Map[String, String]]("uuid")

    val nonExistingUuid = ""
    var validNode = props
    validNode += "uuid" -> uuid

    batchStream << Database.getByUuid(uuid)
    batchStream << Database.getByUuid(nonExistingUuid)
    val testedNodeList = batchStream.execute().asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(1) == null)
    assert(testedNodeList(0).equals(validNode))

    seqStream !! Database.deleteNode(uuid)
  }



  // =================== GET BY LINK ===================

  // not using batch, non-empty output
  "getByLink" should "return a map" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_GET_BY_LINK-1>>"
    val props: Map[String, Any] = Map("key0" -> 1, "link" -> "http://example.com")

    val uuid = (seqStream !! Database.createNode(modelName, relType, props))
      .asInstanceOf[Map[String, String]]("uuid")
    val validNode = (seqStream !! Database.getByUuid(uuid))
      .asInstanceOf[Map[String, Any]]

    val testedNode = (seqStream !! Database.getByLink(modelName, props("link").asInstanceOf[String]))
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    seqStream !! Database.deleteNode(uuid)
  }

  // not using batch, empty output
  it should "return null" in {
    val nonExistingLink = "*abc([)*"
    val testedNode = (seqStream !! Database.getByLink("Content", nonExistingLink))
      .asInstanceOf[Map[String, Any]]

    assert(testedNode == null)
  }

  // using batch, non-empty output
  it should "return a list of not null maps" in {
    val modelName = "Content"
    val relType = "<<TEST_GET_BY_LINK-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "link" -> "http://example2.com")
    val props1: Map[String, Any] = Map("key0" -> "abc", "link" -> "http://example3.com")

    val uuid0 = (seqStream !! Database.createNode(modelName, relType, props0))
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = (seqStream !! Database.createNode(modelName, relType, props1))
      .asInstanceOf[Map[String, String]]("uuid")

    batchStream << Database.getByUuid(uuid0)
    batchStream << Database.getByUuid(uuid1)
    val validNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList = (batchStream
      !! (Database.getByLink("Content", props0("link").asInstanceOf[String])
      << Database.getByLink("Content", props1("link").asInstanceOf[String])))
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(1) != null)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    seqStream !! Database.deleteNode(uuid0)
    seqStream !! Database.deleteNode(uuid1)
  }

  // using batch, empty output
  it should "return a list of mixed not null and null maps" in {
    val modelName = "Content"
    val relType = "<<TEST_GET_BY_LINK-4>>"
    val props: Map[String, Any] = Map("key0" -> 1, "link" -> "http://example4.com")

    val uuid = (seqStream !! Database.createNode(modelName, relType, props))
      .asInstanceOf[Map[String, String]]("uuid")
    val nonExistingLink = "*abc([)*"

    val validNode = (seqStream !! Database.getByUuid(uuid))
      .asInstanceOf[Map[String, Any]]

    batchStream << Database.getByLink("Content", props("link").asInstanceOf[String])
    batchStream << Database.getByLink("Content", nonExistingLink)
    val testedNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList(0) != null)
    assert(testedNodeList(1) == null)
    assert(testedNodeList(0).equals(validNode))

    seqStream !! Database.deleteNode(uuid)
  }



  // =================== GET MODEL NODES ===================

  // not using batch, non-empty output
  "getModelNodes" should "return a list of maps" in {
    val testedNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)

    for (item <- testedNodeList) {
      assert(item.contains("uuid"))
      batchStream << Database.getByUuid(item("uuid").asInstanceOf[String])
    }
    val validNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList.equals(validNodeList))
  }

  // not using batch, empty output
  it should "return null" in {

  }

  // using batch, non-empty output
  it should "return a list of not null lists of maps" in {
    batchStream << Database.getModelNodes()
    batchStream << Database.getModelNodes()

    val testedNodeList = batchStream.execute()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)

    for (item <- testedNodeList(0)) {
      assert(item.contains("uuid"))
      batchStream << Database.getByUuid(item("uuid").asInstanceOf[String])
    }
    val validNodeList = batchStream.execute()
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
    val relType = "<<TEST_GET_CHILDREN-1>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    var modelUuid = ""

    val modelNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    val uuid0 = (seqStream !! Database.createNode(modelName, relType, props0))
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = (seqStream !! Database.createNode(modelName, relType, props1))
      .asInstanceOf[Map[String, String]]("uuid")

    batchStream << Database.getByUuid(uuid0)
    batchStream << Database.getByUuid(uuid1)
    val validNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList = (seqStream !! Database.getChildren(modelUuid, relType))
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

    seqStream !! Database.deleteNode(uuid0)
    seqStream !! Database.deleteNode(uuid1)
  }

  // not using batch, empty output, non-empty props
  it should "return an empty list" in {
    val nonExistingUuid = "*abc([)*"
    val relType = "<<TEST_GET_CHILDREN-2>>"
    val childrenProps: Map[String, Any] = Map("key0" -> 1)

    val testedNodeList = (seqStream !! Database.getChildren(nonExistingUuid, relType, childrenProps))
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)
  }

  // using batch, non-empty output, non-empty props
  it should "return a list of lists of not null maps" in {
    val modelName = "Content"
    val relType = "<<TEST_GET_CHILDREN-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val childrenProps0: Map[String, Any] = Map("key0" -> 1)
    val childrenProps1: Map[String, Any] = Map("key0" -> "abc")
    var modelUuid = ""

    val modelNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    val uuid0 = (seqStream !! Database.createNode(modelName, relType, props0))
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = (seqStream !! Database.createNode(modelName, relType, props1))
      .asInstanceOf[Map[String, String]]("uuid")

    batchStream << Database.getByUuid(uuid0)
    batchStream << Database.getByUuid(uuid1)
    val validNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    batchStream << Database.getChildren(modelUuid, relType, childrenProps0)
    batchStream << Database.getChildren(modelUuid, relType, childrenProps1)
    val testedNodeList = batchStream.execute()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length == 1)
    assert(testedNodeList(1) != null)
    assert(testedNodeList(1).length == 1)
    assert(testedNodeList(0)(0).equals(validNodeList(0)))
    assert(testedNodeList(1)(0).equals(validNodeList(1)))

    seqStream !! Database.deleteNode(uuid0)
    seqStream !! Database.deleteNode(uuid1)
  }

  // using batch, empty output, empty props
  it should "return a list of mixed non-empty and empty lists of maps" in {
    val modelName = "Content"
    val relType = "<<TEST_GET_CHILDREN-4>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    var modelUuid = ""
    val nonExistingUuid = "*abc([)*"

    val modelNodeList = (seqStream !! Database.getModelNodes())
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    val uuid0 = (seqStream !! Database.createNode(modelName, relType, props0))
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = (seqStream !! Database.createNode(modelName, relType, props1))
      .asInstanceOf[Map[String, String]]("uuid")

    batchStream << Database.getByUuid(uuid0)
    batchStream << Database.getByUuid(uuid1)
    val validNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    batchStream << Database.getChildren(nonExistingUuid, relType)
    batchStream << Database.getChildren(modelUuid, relType)
    val testedNodeList = batchStream.execute()
      .asInstanceOf[List[List[Map[String, Any]]]]

    //println(s"$testedNodeList")
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

    seqStream !! Database.deleteNode(uuid0)
    seqStream !! Database.deleteNode(uuid1)
  }



  // =================== GET INSTANCES ===================

  // not using batch, non-empty output, empty props
  "getInstances" should "return a list of maps" in {
    val modelName = "NeoUser"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val uuid0 = (seqStream !! Database.createNode(modelName, relType, props0))
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = (seqStream !! Database.createNode(modelName, relType, props1))
      .asInstanceOf[Map[String, String]]("uuid")

    batchStream << Database.getByUuid(uuid0)
    batchStream << Database.getByUuid(uuid1)
    val validNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    val testedNodeList = (seqStream !! Database.getInstances(modelName))
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

    batchStream << Database.deleteNode(uuid0)
    batchStream << Database.deleteNode(uuid1)
    batchStream.execute()
  }

  // not using batch, empty output, non-empty props
  it should "return an empty list" in {
    val nonExistingModelName = "*abc([)*"
    val childrenProps: Map[String, Any] = Map("key0" -> 1)

    val testedNodeList = (seqStream !! Database.getInstances(nonExistingModelName, childrenProps))
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

    val uuid0 = (seqStream !! Database.createNode(modelName, relType, props0))
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = (seqStream !! Database.createNode(modelName, relType, props1))
      .asInstanceOf[Map[String, String]]("uuid")

    batchStream << Database.getByUuid(uuid0)
    batchStream << Database.getByUuid(uuid1)
    val validNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    batchStream << Database.getInstances(modelName, childrenProps0)
    batchStream << Database.getInstances(modelName, childrenProps1)
    val testedNodeList = batchStream.execute()
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

    batchStream << Database.deleteNode(uuid0)
    batchStream << Database.deleteNode(uuid1)
    batchStream.execute()
  }

  // using batch, empty output, empty props
  it should "return a list of mixed non-empty and empty lists of maps" in {
    val modelName = "Content"
    val relType = "<<INSTANCE>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingModelName = "*abc([)*"

    val uuid0 = (seqStream !! Database.createNode(modelName, relType, props0))
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = (seqStream !! Database.createNode(modelName, relType, props1))
      .asInstanceOf[Map[String, String]]("uuid")

    batchStream << Database.getByUuid(uuid0)
    batchStream << Database.getByUuid(uuid1)
    val validNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    batchStream << Database.getInstances(nonExistingModelName)
    batchStream << Database.getInstances(modelName)
    val testedNodeList = batchStream.execute()
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

    seqStream !! Database.deleteNode(uuid0)
    seqStream !! Database.deleteNode(uuid1)
  }



  // =================== SET PROPERTIES ===================

  // not using batch, correct input
  "setProperties" should "set properties to a node" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_SET_PROPERTIES-1>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet: Map[String, Any] = Map("key1" -> 55, "key2" -> 32)

    seqStream << Database.createNode(modelName, relType, props)
    val uuid = seqStream.execute()
      .asInstanceOf[Map[String, String]]("uuid")

    seqStream !! Database.setProperties(uuid, propsToSet)

    val validNode: Map[String, Any] = Map("uuid" -> uuid, "key0" -> "abc", "key1" -> 55, "key2" -> 32)

    seqStream << Database.getByUuid(uuid)
    val testedNode = seqStream.execute()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    seqStream !! Database.deleteNode(uuid)
  }

  // not using batch, incorrect input
  it should "not set properties to a node" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_SET_PROPERTIES-2>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet: Map[String, Any] = null

    seqStream << Database.createNode(modelName, relType, props)
    val uuid = seqStream.execute()
      .asInstanceOf[Map[String, String]]("uuid")

    var validNode = props
    validNode += "uuid" -> uuid

    seqStream !! Database.setProperties(uuid, propsToSet)

    seqStream << Database.getByUuid(uuid)
    val testedNode = seqStream.execute()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    seqStream !! Database.deleteNode(uuid)
  }

  // using batch, correct input
  it should "set properties to exactly two nodes" in {
    val modelName = "Content"
    val relType = "<<TEST_SET_PROPERTIES-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet0: Map[String, Any] = Map("key1" -> 55, "key2" -> 12)
    val propsToSet1: Map[String, Any] = Map("key1" -> 0, "key2" -> "")

    val uuid0 = (seqStream !! Database.createNode(modelName, relType, props0))
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = (seqStream !! Database.createNode(modelName, relType, props1))
      .asInstanceOf[Map[String, String]]("uuid")

    val validNodeList = List(
      Map("uuid" -> uuid0, "key0" -> 1, "key1" -> 55, "key2" -> 12),
      Map("uuid" -> uuid1, "key0" -> "abc", "key1" -> 0, "key2" -> "")
    )

    batchStream << Database.setProperties(uuid0, propsToSet0)
    batchStream << Database.setProperties(uuid1, propsToSet1)
    batchStream.execute()

    batchStream << Database.getByUuid(uuid0)
    batchStream << Database.getByUuid(uuid1)
    val testedNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    seqStream !! Database.deleteNode(uuid0)
    seqStream !! Database.deleteNode(uuid1)
  }

  // using batch, incorrect input
  it should "set properties only to one node" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_SET_PROPERTIES-4>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet0: Map[String, Any] = null
    val propsToSet1: Map[String, Any] = Map("key1" -> 0, "key2" -> "")

    val uuid0 = (seqStream !! Database.createNode(modelName, relType, props0))
      .asInstanceOf[Map[String, String]]("uuid")
    val uuid1 = (seqStream !! Database.createNode(modelName, relType, props1))
      .asInstanceOf[Map[String, String]]("uuid")

    val validNodeList = List(
      Map("uuid" -> uuid0, "key0" -> 1, "key1" -> "string"),
      Map("uuid" -> uuid1, "key0" -> "abc", "key1" -> 0, "key2" -> "")
    )

    batchStream << Database.setProperties(uuid0, propsToSet0)
    batchStream << Database.setProperties(uuid1, propsToSet1)
    batchStream.execute()

    batchStream << Database.getByUuid(uuid0)
    batchStream << Database.getByUuid(uuid1)
    val testedNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    seqStream !! Database.deleteNode(uuid0)
    seqStream !! Database.deleteNode(uuid1)
  }



  // =================== DELETE PROPERTIES ===================

  // not using batch, correct input
  "deleteProperties" should "delete node's properties" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_DELETE_PROPERTIES-1>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToDelete: List[String] = List("key1")

    seqStream << Database.createNode(modelName, relType, props)
    val uuid = seqStream.execute()
      .asInstanceOf[Map[String, String]]("uuid")

    seqStream !! Database.deleteProperties(uuid, propsToDelete)

    val validNode: Map[String, Any] = Map("uuid" -> uuid, "key0" -> "abc")

    seqStream << Database.getByUuid(uuid)
    val testedNode = seqStream.execute()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    seqStream !! Database.deleteNode(uuid)
  }

  // not using batch, incorrect input
  it should "not delete node's properties" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_DELETE_PROPERTIES-2>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToDelete: List[String] = List("nonExistingKey")

    seqStream << Database.createNode(modelName, relType, props)
    val uuid = seqStream.execute()
      .asInstanceOf[Map[String, String]]("uuid")

    var validNode = props
    validNode += "uuid" -> uuid

    seqStream !! Database.deleteProperties(uuid, propsToDelete)

    seqStream << Database.getByUuid(uuid)
    val testedNode = seqStream.execute()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    seqStream !! Database.deleteNode(uuid)
  }

  // using batch, correct input
  it should "delete properties of exactly two nodes" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_PROPERTIES-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToDelete0: List[String] = List("key0")
    val propsToDelete1: List[String] = List("key1")

    seqStream << (Database.createNode(modelName, relType, props0)
      << Database.createNode(modelName, relType, props1))
    val uuidList = seqStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = List(
      Map("uuid" -> uuidList(0)("uuid"), "key1" -> "string"),
      Map("uuid" -> uuidList(1)("uuid"), "key0" -> "abc")
    )

    batchStream << Database.deleteProperties(uuidList(0)("uuid"), propsToDelete0)
    batchStream << Database.deleteProperties(uuidList(1)("uuid"), propsToDelete1)
    batchStream.execute()

    batchStream << Database.getByUuid(uuidList(0)("uuid"))
    batchStream << Database.getByUuid(uuidList(1)("uuid"))
    val testedNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    seqStream !! Database.deleteNode(uuidList(0)("uuid"))
    seqStream !! Database.deleteNode(uuidList(1)("uuid"))
  }

  // using batch, incorrect input
  it should "delete properties of only one node" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_DELETE_PROPERTIES-4>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToDelete0: List[String] = List("nonExistingKey")
    val propsToDelete1: List[String] = List("key1")

    seqStream << (Database.createNode(modelName, relType, props0)
      << Database.createNode(modelName, relType, props1))
    val uuidList = seqStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = List(
      Map("uuid" -> uuidList(0)("uuid"), "key0" -> 1, "key1" -> "string"),
      Map("uuid" -> uuidList(1)("uuid"), "key0" -> "abc")
    )

    batchStream << Database.deleteProperties(uuidList(0)("uuid"), propsToDelete0)
    batchStream << Database.deleteProperties(uuidList(1)("uuid"), propsToDelete1)
    batchStream.execute()

    batchStream << Database.getByUuid(uuidList(0)("uuid"))
    batchStream << Database.getByUuid(uuidList(1)("uuid"))
    val testedNodeList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 2)
    assert(testedNodeList(0).equals(validNodeList(0)))
    assert(testedNodeList(1).equals(validNodeList(1)))

    seqStream !! Database.deleteNode(uuidList(0)("uuid"))
    seqStream !! Database.deleteNode(uuidList(1)("uuid"))
  }



  // =================== CREATE NODE ===================

  // not using batch, correct input
  "createNode" should "create a node with properties" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_NODE-1>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    seqStream << Database.createNode(modelName, relType, props)
    val uuid = seqStream.execute()
      .asInstanceOf[Map[String, String]]("uuid")

    var validNode = props
    validNode += "uuid" -> uuid

    seqStream << Database.getByUuid(uuid)
    val testedNode = seqStream.execute()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode != null)
    assert(testedNode.equals(validNode))

    seqStream !! Database.deleteNode(uuid)
  }

  // not using batch, incorrect input
  it should "not create any node" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_NODE-2>>"
    val props: Map[String, Any] = Map()

    seqStream << Database.createNode(modelName, relType, props)
    val uuid = seqStream.execute()
      .asInstanceOf[Map[String, String]]("uuid")

    assert(uuid == null)
  }

  // using batch, correct input
  it should "create exactly two nodes with properties" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_NODE-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    var modelUuid = ""

    seqStream << Database.getModelNodes()
    val modelNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    assert(uuidList != null)
    assert(uuidList.length == 2)

    val validNodeList = ListBuffer(props0, props1)
    validNodeList(0) += "uuid" -> uuidList(0)("uuid")
    validNodeList(1) += "uuid" -> uuidList(1)("uuid")

    seqStream << Database.getChildren(modelUuid, relType)
    val testedNodeList = seqStream.execute()
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

    seqStream !! Database.deleteNode(uuidList(0)("uuid"))
    seqStream !! Database.deleteNode(uuidList(1)("uuid"))
  }

  // using batch, incorrect input
  it should "create only one node with properties" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_CREATE_NODE-4>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = null

    var modelUuid = ""

    seqStream << Database.getModelNodes()
    val modelNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(uuidList != null)
    assert(uuidList.length == 2)
    assert(uuidList(0) != null)
    assert(uuidList(1) != null)
    assert(uuidList(0)("uuid") != null)
    assert(uuidList(1)("uuid") == null)

    var validNode = props0
    validNode += "uuid" -> uuidList(0)("uuid")

    seqStream << Database.getChildren(modelUuid, relType)
    val testedNodeList = seqStream.execute()
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

    seqStream !! Database.deleteNode(uuidList(0)("uuid").asInstanceOf[String])
    seqStream !! Database.deleteNode(uuidList(1)("uuid").asInstanceOf[String])
  }



  // =================== DELETE NODE ===================

  // not using batch, correct input
  "deleteNode" should "delete a node" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_NODE-1>>"
    val props: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    seqStream << Database.createNode(modelName, relType, props)
    val uuid = seqStream.execute()
      .asInstanceOf[Map[String, String]]("uuid")

    seqStream !! Database.deleteNode(uuid)

    seqStream << Database.getByUuid(uuid)
    val testedNode = seqStream.execute()
      .asInstanceOf[Map[String, Any]]

    assert(testedNode == null)
  }

  // not using batch, incorrect input
  it should "not delete any node" in {

  }

  // using batch, correct input
  it should "delete exactly two nodes" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_NODE-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    var modelUuid = ""

    seqStream << Database.getModelNodes()
    val modelNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    for (item <- modelNodeList) {
      if (item("model_name").asInstanceOf[String] == modelName) {
        modelUuid = item("uuid").asInstanceOf[String]
      }
    }

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()

    val validNodeList = ListBuffer(props0, props1)
    validNodeList(0) += "uuid" -> uuidList(0)("uuid")
    validNodeList(1) += "uuid" -> uuidList(1)("uuid")

    seqStream << Database.getChildren(modelUuid, relType)
    val testedNodeList = seqStream.execute()
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
    val relType = "<<TEST_CREATE_RELATIONSHIP-1>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2")
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNode))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()
  }

  // not using batch, incorrect input, non-empty props
  it should "not create any relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_RELATIONSHIP-2>>"
    val props: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")

    val nonExistingUuid = "*abc([)*"
    val relProps: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")

    seqStream << Database.createNode(modelName, relType, props)
    val uuid = seqStream.execute()
      .asInstanceOf[Map[String, String]]("uuid")

    seqStream !! Database.createRelationship(uuid, nonExistingUuid, relType + "2", relProps)

    seqStream << Database.getChildren(uuid, relType + "2")
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)

    seqStream !! Database.deleteNode(uuid)
  }

  // using batch, correct input, non-empty props
  it should "create exactly two relationships with properties" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_RELATIONSHIP-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relProps0: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val relProps1: Map[String, Any] = Map("keyA" -> "aba", "keyB" -> "aab")

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    batchStream << Database.createNode(modelName, relType, props2)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps0)
    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2", relProps1)
    batchStream.execute()

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2")
    val testedNodeList = seqStream.execute()
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

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream << Database.deleteNode(uuidList(2)("uuid"))
    batchStream.execute()
  }

  // using batch, incorrect input, empty props
  it should "create only one relationship without properties" in {
    val modelName = "Content"
    val relType = "<<TEST_CREATE_RELATIONSHIP-4>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingUuid = "*abc([)*"

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batchStream << Database.createRelationship(uuidList(0)("uuid"), nonExistingUuid, relType + "2")
    batchStream.execute()

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2")
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNode))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()
  }



  // =================== DELETE RELATIONSHIP ===================

  // not using batch, correct input
  "deleteRelationship" should "delete a relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP-1>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    seqStream !! Database.deleteRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"))

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2")
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()
  }

  // not using batch, incorrect input
  it should "not delete any relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP-2>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingUuid = "*abc([)*"

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    seqStream !! Database.deleteRelationship(uuidList(0)("uuid"), nonExistingUuid)

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2")
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNode))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()
  }

  // using batch, correct input
  it should "delete exactly two relationships" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    batchStream << Database.createNode(modelName, relType, props2)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2")
    batchStream.execute()

    batchStream << Database.deleteRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"))
    batchStream << Database.deleteRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"))
    batchStream.execute()

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2")
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream << Database.deleteNode(uuidList(2)("uuid"))
    batchStream.execute()
  }

  // using batch, incorrect input
  it should "delete only one relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP-4>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val nonExistingUuid = "*abc([)*"

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    batchStream << Database.createNode(modelName, relType, props2)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2")
    batchStream.execute()

    batchStream << Database.deleteRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"))
    batchStream << Database.deleteRelationship(uuidList(0)("uuid"), nonExistingUuid)
    batchStream.execute()

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2")
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)
    assert(testedNodeList(0).equals(validNodeList(1)))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream << Database.deleteNode(uuidList(2)("uuid"))
    batchStream.execute()
  }



  // =================== SET RELATIONSHIP PROPERTIES ===================

  // not using batch, correct input
  "setRelationshipProperties" should "set properties to a relationship" in {
    val modelName = "Content"
    val relType = "<<TEST_SET_RELATIONSHIP_PROPERTIES-1>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val propsToSet: Map[String, Any] = Map("relKey" -> 92)

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    seqStream !! Database.setRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), propsToSet)

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2")
    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), propsToSet)
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length == 1)
    assert(testedNodeList(0)(0).equals(validNode))

    assert(testedNodeList(0).equals(testedNodeList(1)))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()
  }

  // not using batch, incorrect input
  it should "not set properties to a relationship" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_SET_RELATIONSHIP_PROPERTIES-2>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingUuid = "*abc([)*"
    val relProps: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val propsToSet: Map[String, Any] = Map("relKey" -> 92)

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), nonExistingUuid, relType + "2", relProps)
    seqStream !! Database.setRelationshipProperties(uuidList(0)("uuid"), nonExistingUuid, propsToSet)
    seqStream !! Database.setRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), null)

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", propsToSet)
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 0)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()
  }

  // using batch, correct input
  it should "set properties to exactly two relationships" in {
    val modelName = "Content"
    val relType = "<<TEST_SET_RELATIONSHIP_PROPERTIES-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relPropsToSet0: Map[String, Any] = Map("relKey" -> 92)
    val relPropsToSet1: Map[String, Any] = Map("relKey" -> 78)

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    batchStream << Database.createNode(modelName, relType, props2)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2")
    batchStream.execute()

    batchStream << Database.setRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), relPropsToSet0)
    batchStream << Database.setRelationshipProperties(uuidList(0)("uuid"), uuidList(2)("uuid"), relPropsToSet1)
    batchStream.execute()

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relPropsToSet0)
    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relPropsToSet1)
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length == 1)
    assert(testedNodeList(0)(0).equals(validNodeList(0)))

    assert(testedNodeList(1) != null)
    assert(testedNodeList(1).length == 1)
    assert(testedNodeList(1)(0).equals(validNodeList(1)))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream << Database.deleteNode(uuidList(2)("uuid"))
    batchStream.execute()
  }

  // using batch, incorrect input
  it should "set properties only to one relationship" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_SET_RELATIONSHIP_PROPERTIES-4>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relPropsToSet0: Map[String, Any] = Map("relKey" -> 92)
    val relPropsToSet1: Map[String, Any] = null

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    batchStream << Database.createNode(modelName, relType, props2)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2")
    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2")
    batchStream.execute()

    batchStream << Database.setRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), relPropsToSet0)
    batchStream << Database.setRelationshipProperties(uuidList(0)("uuid"), uuidList(2)("uuid"), relPropsToSet1)
    batchStream.execute()

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relPropsToSet0)
    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relPropsToSet1)
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length == 1)
    assert(testedNodeList(0)(0).equals(validNodeList(0)))

    assert(testedNodeList(1) != null)
    assert(testedNodeList(1).length == 2)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream << Database.deleteNode(uuidList(2)("uuid"))
    batchStream.execute()
  }



  // =================== DELETE RELATIONSHIP PROPERTIES ===================

  // not using batch, correct input
  "deleteRelationshipProperties" should "delete relationship's properties" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP_PROPERTIES-1>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val relProps: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val propsToDelete: List[String] = List("keyB")

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    var validNode = props1
    validNode += "uuid" -> uuidList(1)("uuid")

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps)
    seqStream !! Database.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), propsToDelete)

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2")
    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relProps)
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length == 1)
    assert(testedNodeList(0)(0).equals(validNode))

    assert(testedNodeList(1) != null)
    assert(testedNodeList(1).length == 0)

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()
  }

  // not using batch, incorrect input
  it should "not delete relationship's properties" in {
    val modelName = "ContentSource"
    val relType = "<<TEST_DELETE_RELATIONSHIP_PROPERTIES-2>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)

    val nonExistingUuid = "*abc([)*"
    val relProps: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val propsToDelete: List[String] = List("keyB")

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    seqStream !! Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps)

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relProps)
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    seqStream !! Database.deleteRelationshipProperties(uuidList(0)("uuid"), nonExistingUuid, propsToDelete)
    seqStream !! Database.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), null)

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relProps)
    val testedNodeList2 = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    assert(testedNodeList != null)
    assert(testedNodeList.length == 1)

    assert(testedNodeList2 != null)
    assert(testedNodeList2.length == 1)
    assert(testedNodeList.equals(testedNodeList2))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream.execute()
  }

  // using batch, correct input
  it should "delete properties of exactly two relationships" in {
    val modelName = "Content"
    val relType = "<<TEST_DELETE_RELATIONSHIP_PROPERTIES-3>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relProps0: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val relProps1: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "bca")

    val relPropsToDelete0: List[String] = List("keyA")
    val relPropsToDelete1: List[String] = List("keyB")

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    batchStream << Database.createNode(modelName, relType, props2)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    val validProps0: Map[String, Any] = Map("keyB" -> "aaa")
    val validProps1: Map[String, Any] = Map("keyA" -> 5)

    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps0)
    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2", relProps1)
    batchStream.execute()

    batchStream << Database.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), relPropsToDelete0)
    batchStream << Database.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(2)("uuid"), relPropsToDelete1)
    batchStream.execute()

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), validProps0)
    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), validProps1)
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList(0) != null)
    assert(testedNodeList(0).length == 1)
    assert(testedNodeList(0)(0).equals(validNodeList(0)))

    assert(testedNodeList(1) != null)
    assert(testedNodeList(1).length == 1)
    assert(testedNodeList(1)(0).equals(validNodeList(1)))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream << Database.deleteNode(uuidList(2)("uuid"))
    batchStream.execute()
  }

  // using batch, incorrect input
  it should "delete properties of only one relationship" in {
    val modelName = "NeoUser"
    val relType = "<<TEST_DELETE_RELATIONSHIP_PROPERTIES-4>>"
    val props0: Map[String, Any] = Map("key0" -> 1, "key1" -> "string")
    val props1: Map[String, Any] = Map("key0" -> "abc", "key1" -> 33)
    val props2: Map[String, Any] = Map("key0" -> "aaa", "key1" -> 15)

    val relProps0: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "aaa")
    val relProps1: Map[String, Any] = Map("keyA" -> 5, "keyB" -> "bca")

    val relPropsToDelete0: List[String] = null
    val relPropsToDelete1: List[String] = List("keyB")

    batchStream << Database.createNode(modelName, relType, props0)
    batchStream << Database.createNode(modelName, relType, props1)
    batchStream << Database.createNode(modelName, relType, props2)
    val uuidList = batchStream.execute()
      .asInstanceOf[List[Map[String, String]]]

    val validNodeList = ListBuffer(props1, props2)
    validNodeList(0) += "uuid" -> uuidList(1)("uuid")
    validNodeList(1) += "uuid" -> uuidList(2)("uuid")

    val validProps1: Map[String, Any] = Map("keyA" -> 5)

    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(1)("uuid"), relType + "2", relProps0)
    batchStream << Database.createRelationship(uuidList(0)("uuid"), uuidList(2)("uuid"), relType + "2", relProps1)
    batchStream.execute()

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map())
    val testedNodeList = seqStream.execute()
      .asInstanceOf[List[Map[String, Any]]]

    batchStream << Database.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(1)("uuid"), relPropsToDelete0)
    batchStream << Database.deleteRelationshipProperties(uuidList(0)("uuid"), uuidList(2)("uuid"), relPropsToDelete1)
    batchStream.execute()

    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), relProps0)
    seqStream << Database.getChildren(uuidList(0)("uuid"), relType + "2", Map(), validProps1)
    val testedNodeList2 = seqStream.execute()
      .asInstanceOf[List[List[Map[String, Any]]]]

    assert(testedNodeList2(0) != null)
    assert(testedNodeList2(0).length == 1)
    assert(testedNodeList2(0)(0).equals(validNodeList(0)))

    assert(testedNodeList2(1) != null)
    assert(testedNodeList2(1).length == 2)
    assert(testedNodeList.equals(testedNodeList2(1)))

    batchStream << Database.deleteNode(uuidList(0)("uuid"))
    batchStream << Database.deleteNode(uuidList(1)("uuid"))
    batchStream << Database.deleteNode(uuidList(2)("uuid"))
    batchStream.execute()
  }
}
