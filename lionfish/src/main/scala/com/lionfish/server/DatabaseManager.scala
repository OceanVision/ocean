package com.lionfish.server

import java.util.UUID
import scala.collection.mutable.ListBuffer
import org.neo4j.graphdb.factory.GraphDatabaseFactory
import org.neo4j.graphdb._
import org.neo4j.cypher.{ExecutionEngine, ExecutionResult}
import org.neo4j.tooling.GlobalGraphOperations

// TODO: logging, nicer way of handling errors

object DatabaseManager {
  private val DB_PATH = "/usr/lib/neo4j/data/graph.db" // TODO: consider SCALA_HOME in some way
  private val graphDB = new GraphDatabaseFactory().newEmbeddedDatabase(DB_PATH)

  private val globalOperations = GlobalGraphOperations.at(graphDB)
  private val cypherEngine = new ExecutionEngine(graphDB)
  private var cypherResult: ExecutionResult = null

  private var modelNodes: Map[String, Node] = Map()
  initCache()

  private def parseNodeToMap(node: Node): Map[String, Any] = {
    try {
      val keys = node.getPropertyKeys
      var map: Map[String, Any] = Map()
      val it = keys.iterator()
      while (it.hasNext) {
        val key: String = it.next()
        map += key -> node.getProperty(key)
      }
      map
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Parsing node to map failed at line $line. Error message: $e")
      }
      null
    }
  }

  private def parseNodeToSet(node: Node): Set[(String, Any)] = {
    try {
      val keys = node.getPropertyKeys
      var set: Set[(String, Any)] = Set()
      val it = keys.iterator()
      while (it.hasNext) {
        val key: String = it.next()
        set += Tuple2(key, node.getProperty(key))
      }
      set
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Parsing node to set failed at line $line. Error message: $e")
      }
        null
    }
  }

  private def executeCypher(query: String, params: Map[String, Any] = Map()): List[List[Any]] = {
    try {
      cypherResult = cypherEngine.execute(query, params)
      var parsedResult: ListBuffer[List[Any]] = ListBuffer()
      for (row: Map[String, Any] <- cypherResult) {
        var rowItems: ListBuffer[Any] = ListBuffer()
        for (column <- row) {
          // TODO: Do not assume that every value is Node
          rowItems += parseNodeToMap(column._2.asInstanceOf[Node])
        }
        parsedResult += rowItems.toList
      }

      parsedResult.toList
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Executing Cypher script failed at line $line. Error message: $e")
      }
      null
    }
  }

  private def initCache() = {
    try {
      // Simply gets model nodes
      val tx = graphDB.beginTx()
      val rawResult = globalOperations.getAllNodesWithLabel(DynamicLabel.label("Model"))
      tx.success()

      // Saves result
      val it = rawResult.iterator()
      while (it.hasNext) {
        val node = it.next()
        modelNodes += node.getProperty("model_name").asInstanceOf[String] -> node
      }
      it.close()
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Initialising cache failed at line $line. Error message: $e")
      }
    }
  }

  def getByUuid(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()

      // Gets nodes by uuid
      for (item <- args) {
        // Extracts result
        val rawNode = graphDB.findNodesByLabelAndProperty(
          DynamicLabel.label("Node"),
          "uuid",
          item("uuid")
        )
        val it = rawNode.iterator()
        if (it.hasNext) {
          rawResult += parseNodeToMap(it.next())
        } else {
          rawResult += null
        }
        it.close()
      }
      tx.success()
      result = rawResult.toList
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
        result = List()
    } finally {
      tx.close()
    }

    result
  }

  def getByLink(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()

      // Gets nodes by uuid
      for (item <- args) {
        // Extracts result
        val rawNode = graphDB.findNodesByLabelAndProperty(
          DynamicLabel.label(item("modelName").asInstanceOf[String]),
          "link",
          item("link")
        )
        val it = rawNode.iterator()
        if (it.hasNext) {
          rawResult += parseNodeToMap(it.next())
        } else {
          rawResult += null
        }
        it.close()
      }
      tx.success()
      result = rawResult.toList
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
        result = List()
    } finally {
      tx.close()
    }

    result
  }

  def getModelNodes(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()

      // Simply gets model nodes
      val rawModelNodes = globalOperations.getAllNodesWithLabel(DynamicLabel.label("Model"))
      tx.success()

      // Extracts result
      val it = rawModelNodes.iterator()
      while (it.hasNext) {
        rawResult += parseNodeToMap(it.next())
      }

      result = List.fill[Any](args.length)(rawResult.toList)
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
        result = List()
    } finally {
      tx.close()
    }

    result
  }

  def getChildren(args: List[Map[String, Any]]): List[Any] = {
    var result: List[List[Map[String, Any]]] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[List[Map[String, Any]]] = ListBuffer()
      val label = DynamicLabel.label("Node")

      for (item <- args) {
        // Gets each node as an instance of Node
        val rawParentNode = graphDB.findNodesByLabelAndProperty(
          label,
          "uuid",
          item("parentUuid").asInstanceOf[String]
        )

        val props = item("childrenProps")
          .asInstanceOf[Map[String, Any]]
          .toSet[(String, Any)]

        val it = rawParentNode.iterator()
        if (it.hasNext) {
          val childrenOfOneNode: ListBuffer[Map[String, Any]] = ListBuffer()
          val parentNode = it.next()

          // Gets all outgoing relationships of given type
          val relType = DynamicRelationshipType.withName(item("relType").asInstanceOf[String])
          val relList = parentNode.getRelationships(relType, Direction.OUTGOING).iterator()

          // Gets children and extracts partial result
          while (relList.hasNext) {
            val node = parseNodeToSet(relList.next().getEndNode)

            // TODO: make it more efficient
            if (props.subsetOf(node)) {
              childrenOfOneNode += node.toMap[String, Any]
            }
          }

          rawResult += childrenOfOneNode.toList
        } else {
          rawResult += List()
        }
      }
      tx.success()
      result = rawResult.toList
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
        result = List()
    } finally {
      tx.close()
    }

    result
  }

  def getInstances(args: List[Map[String, Any]]): List[Any] = {
    var result: List[List[Map[String, Any]]] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[List[Map[String, Any]]] = ListBuffer()
      val label = DynamicLabel.label("Model")

      for (item <- args) {
        // Gets each node as an instance of Node
        val rawParentNode = graphDB.findNodesByLabelAndProperty(
          label,
          "model_name",
          item("modelName").asInstanceOf[String]
        )

        val props = item("childrenProps")
          .asInstanceOf[Map[String, Any]]
          .toSet[(String, Any)]

        val it = rawParentNode.iterator()
        if (it.hasNext) {
          val instancesOfOneNode: ListBuffer[Map[String, Any]] = ListBuffer()
          val parentNode = it.next()

          // Gets all outgoing relationships of type <<INSTANCE>>
          val relType = DynamicRelationshipType.withName("<<INSTANCE>>")
          val relList = parentNode.getRelationships(relType, Direction.OUTGOING).iterator()

          // Gets children and extracts partial result
          while (relList.hasNext) {
            val node = parseNodeToSet(relList.next().getEndNode)

            // TODO: make it more efficient
            if (props.subsetOf(node)) {
              instancesOfOneNode += node.toMap[String, Any]
            }
          }

          rawResult += instancesOfOneNode.toList
        } else {
          rawResult += List()
        }
      }
      tx.success()
      result = rawResult.toList
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
        result = List()
    } finally {
      tx.close()
    }

    result
  }

  def setProperties(args: List[Map[String, Any]]): List[Any] = {
    val tx = graphDB.beginTx()
    try {
      val nodeLabel = DynamicLabel.label("Node")

      for (item <- args) {
        val props = item("props").asInstanceOf[Map[String, Any]]

        if (props != null && !props.isEmpty) {
          // Gets each node as an instance of Node
          val rawNode = graphDB.findNodesByLabelAndProperty(
            nodeLabel,
            "uuid",
            item("uuid").asInstanceOf[String]
          )

          val it = rawNode.iterator()
          if (it.hasNext) {
            val node = it.next()

            // Sets properties to the node
            for ((key, value) <- props) {
              node.setProperty(key, value)
            }
          }
        }
      }
      tx.success()
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
    } finally {
      tx.close()
    }

    null
  }

  def deleteProperties(args: List[Map[String, Any]]): List[Any] = {
    val tx = graphDB.beginTx()
    try {
      val nodeLabel = DynamicLabel.label("Node")

      for (item <- args) {
        val keys = item("propertyKeys").asInstanceOf[List[String]]

        if (keys != null && !keys.isEmpty) {
          // Gets each node as an instance of Node
          val rawNode = graphDB.findNodesByLabelAndProperty(
            nodeLabel,
            "uuid",
            item("uuid").asInstanceOf[String]
          )

          val it = rawNode.iterator()
          if (it.hasNext) {
            val node = it.next()

            // Delete node's properties
            for (key <- keys) {
              node.removeProperty(key)
            }
          }
        }
      }
      tx.success()
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
    } finally {
      tx.close()
    }

    null
  }

  // TODO: Add defaults
  def createNodes(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Map[String, Any]] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Map[String, Any]] = ListBuffer()

      // Creates nodes by given properties
      for (params <- args) {
        val uuid = UUID.randomUUID().toString
        var props = params("props").asInstanceOf[Map[String, Any]]

        if (props != null && !props.isEmpty) {
          props += "uuid" -> uuid
          rawResult += Map("uuid" -> uuid)

          val node = graphDB.createNode()
          for ((key, value) <- props) {
            node.setProperty(key, value)
          }

          val modelName = params("modelName").asInstanceOf[String]
          node.addLabel(DynamicLabel.label("Node"))
          node.addLabel(DynamicLabel.label(modelName))

          val relType = DynamicRelationshipType.withName(params("relType").asInstanceOf[String])
          modelNodes(modelName).createRelationshipTo(node, relType)
        } else {
          rawResult += Map("uuid" -> null)
        }
      }
      tx.success()
      result = rawResult.toList
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
        result = List()
    } finally {
      tx.close()
    }

    result
  }

  def deleteNodes(args: List[Map[String, Any]]): List[Any] = {
    // Prepares params
    var nodeUuidList: ListBuffer[String] = ListBuffer()
    for (item <- args) {
      nodeUuidList += item("uuid").asInstanceOf[String]
    }

    val tx = graphDB.beginTx()
    try {
      // Builds query and executes
      val query =
        "MATCH (e:Node)-[r]-() " +
        "WHERE e.uuid IN {uuid_list} " +
        "DELETE e, r"
      executeCypher(query, Map("uuid_list" -> nodeUuidList.toList))
      tx.success()
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
    } finally {
      tx.close()
    }

    null
  }

  def createRelationships(args: List[Map[String, Any]]): List[Any] = {
    val tx = graphDB.beginTx()
    try {
      val nodeLabel = DynamicLabel.label("Node")

      for (item <- args) {
        // Gets each pair of nodes as instances of Node
        val rawStartNode = graphDB.findNodesByLabelAndProperty(
          nodeLabel,
          "uuid",
          item("startNodeUuid").asInstanceOf[String]
        )

        val rawEndNode = graphDB.findNodesByLabelAndProperty(
          nodeLabel,
          "uuid",
          item("endNodeUuid").asInstanceOf[String]
        )

        val it1 = rawStartNode.iterator()
        val it2 = rawEndNode.iterator()
        if (it1.hasNext && it2.hasNext) {
          val startNode = it1.next()
          val endNode = it2.next()
          val relType = DynamicRelationshipType.withName(item("relType").asInstanceOf[String])

          // Creates a relationship of a given type
          val rel = startNode.createRelationshipTo(endNode, relType)

          // Sets properties to the relationship
          for ((key, value) <- item("props").asInstanceOf[Map[String, Any]]) {
            rel.setProperty(key, value)
          }
        }
      }
      tx.success()
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
    } finally {
      tx.close()
    }

    null
  }

  def deleteRelationships(args: List[Map[String, Any]]): List[Any] = {
    val tx = graphDB.beginTx()
    try {
      val nodeLabel = DynamicLabel.label("Node")

      for (item <- args) {
        // Gets each start node as an instance of Node
        val rawStartNode = graphDB.findNodesByLabelAndProperty(
          nodeLabel,
          "uuid",
          item("startNodeUuid").asInstanceOf[String]
        )

        val it = rawStartNode.iterator()
        if (it.hasNext) {
          val startNode = it.next()
          val endNodeUuid = item("endNodeUuid").asInstanceOf[String]

          // Looks through a list of relationships to delete a proper one
          val relList = startNode.getRelationships(Direction.OUTGOING).iterator()
          while (relList.hasNext) {
            val rel = relList.next()
            if (endNodeUuid == rel.getEndNode.getProperty("uuid").asInstanceOf[String]) {
              rel.delete()
            }
          }
        }
      }
      tx.success()
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
    } finally {
      tx.close()
    }

    null
  }

  def setRelationshipProperties(args: List[Map[String, Any]]): List[Any] = {
    val tx = graphDB.beginTx()
    try {
      val nodeLabel = DynamicLabel.label("Node")

      for (item <- args) {
        // Gets each start node as an instance of Node
        val rawStartNode = graphDB.findNodesByLabelAndProperty(
          nodeLabel,
          "uuid",
          item("startNodeUuid").asInstanceOf[String]
        )

        val it = rawStartNode.iterator()
        if (it.hasNext) {
          val startNode = it.next()
          val endNodeUuid = item("endNodeUuid").asInstanceOf[String]

          // Looks through a list of relationships to delete a proper one
          val relList = startNode.getRelationships(Direction.OUTGOING).iterator()
          while (relList.hasNext) {
            val rel = relList.next()
            if (endNodeUuid == rel.getEndNode.getProperty("uuid").asInstanceOf[String]) {
              // Sets properties to the relationship
              for ((key, value) <- item("props").asInstanceOf[Map[String, Any]]) {
                rel.setProperty(key, value)
              }
            }
          }
        }
      }
      tx.success()
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
    } finally {
      tx.close()
    }

    null
  }

  def deleteRelationshipProperties(args: List[Map[String, Any]]): List[Any] = {
    val tx = graphDB.beginTx()
    try {
      val nodeLabel = DynamicLabel.label("Node")

      for (item <- args) {
        // Gets each start node as an instance of Node
        val rawStartNode = graphDB.findNodesByLabelAndProperty(
          nodeLabel,
          "uuid",
          item("startNodeUuid").asInstanceOf[String]
        )

        val it = rawStartNode.iterator()
        if (it.hasNext) {
          val startNode = it.next()
          val endNodeUuid = item("endNodeUuid").asInstanceOf[String]

          // Looks through a list of relationships to delete a proper one
          val relList = startNode.getRelationships(Direction.OUTGOING).iterator()
          while (relList.hasNext) {
            val rel = relList.next()
            if (endNodeUuid == rel.getEndNode.getProperty("uuid").asInstanceOf[String]) {
              // Delete relationship's properties
              for (key <- item("props").asInstanceOf[List[String]]) {
                rel.removeProperty(key)
              }
            }
          }
        }
      }
      tx.success()
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Failed to execute the function at line $line. Error message: $e")
      }
        tx.failure()
    } finally {
      tx.close()
    }

    null
  }
}
