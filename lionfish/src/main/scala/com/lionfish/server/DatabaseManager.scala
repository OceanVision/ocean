package com.lionfish.server

import java.util.UUID
import scala.collection.mutable.ListBuffer
import org.neo4j.graphdb.factory.GraphDatabaseFactory
import org.neo4j.graphdb._
import org.neo4j.cypher.{ExecutionEngine, ExecutionResult}
import org.neo4j.tooling.GlobalGraphOperations
import org.neo4j.server.WrappingNeoServerBootstrapper
import org.neo4j.kernel.GraphDatabaseAPI
import org.neo4j.kernel._
import org.neo4j.server._
import org.neo4j.server.configuration._
import org.neo4j.server.database._
import org.neo4j.server.preflight._
import com.lionfish.utils.Config

// TODO: logging, nicer way of handling errors

object DatabaseManager {
  val databasePath = "/data/graph.db"
  var neo4jPath = Config.defaultNeo4jPath
  var neo4jConsolePort = Config.defaultNeo4jConsolePort
  val graphDB = new GraphDatabaseFactory().newEmbeddedDatabase(neo4jPath + databasePath)

  val globalOperations = GlobalGraphOperations.at(graphDB)
  val cypherEngine = new ExecutionEngine(graphDB)
  var cypherResult: ExecutionResult = null

  def initNeo4jConsole() {
    val config = new ServerConfigurator(graphDB.asInstanceOf[GraphDatabaseAPI])
    config.configuration().setProperty(
      Configurator.WEBSERVER_PORT_PROPERTY_KEY, neo4jConsolePort
    )

    config.configuration().setProperty(
      Configurator.HTTP_LOGGING, Configurator.DEFAULT_HTTP_LOGGING
    )

    val srv = new WrappingNeoServerBootstrapper(graphDB.asInstanceOf[GraphDatabaseAPI], config)
    srv.start()
  }

  def setNeo4jPath(path: String) = {
    neo4jPath = path
  }

  def setNeo4jConsolePort(port: Int) = {
    neo4jConsolePort = port
  }

  private def parseMap(node: Node): Map[String, Any] = {
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

  private def parseMap(rel: Relationship): Map[String, Any] = {
    try {
      val keys = rel.getPropertyKeys
      var map: Map[String, Any] = Map()
      val it = keys.iterator()
      while (it.hasNext) {
        val key: String = it.next()
        map += key -> rel.getProperty(key)
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

  private def parseSet(node: Node): Set[(String, Any)] = {
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

  private def parseSet(rel: Relationship): Set[(String, Any)] = {
    try {
      val keys = rel.getPropertyKeys
      var set: Set[(String, Any)] = Set()
      val it = keys.iterator()
      while (it.hasNext) {
        val key: String = it.next()
        set += Tuple2(key, rel.getProperty(key))
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
          column._2 match {
            case node: Node => {
              rowItems += parseMap(node)
            }
            case rel: Relationship => {
              rowItems += parseMap(rel)
            }
            case sth: Any => {
              rowItems += sth
            }
          }
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

  def executeQuery(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()

      for (item <- args) {
        val query = item("query").asInstanceOf[String]
        val params = item("parameters").asInstanceOf[Map[String, Any]]

        // Executes query
        val returnedData = executeCypher(query, params)
        rawResult += returnedData
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

  def getByUuid(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()
      val label = DynamicLabel.label("Node")

      // Gets nodes by uuid
      for (item <- args) {
        // Extracts result
        val uuid = item("uuid").asInstanceOf[String]
        val rawNode = graphDB.findNodesByLabelAndProperty(label, "uuid", uuid)

        val it = rawNode.iterator()
        if (it.hasNext) {
          rawResult += parseMap(it.next())
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
        val label = DynamicLabel.label(item("modelName").asInstanceOf[String])
        val link = item("link").asInstanceOf[String]
        val rawNode = graphDB.findNodesByLabelAndProperty(label, "link", link)

        val it = rawNode.iterator()
        if (it.hasNext) {
          rawResult += parseMap(it.next())
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

  def getByTag(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()
      val label = DynamicLabel.label("Tag")

      // Gets nodes by uuid
      for (item <- args) {
        // Extracts result
        val tag = item("tag").asInstanceOf[String]
        val rawNode = graphDB.findNodesByLabelAndProperty(label, "tag", tag)

        val it = rawNode.iterator()
        if (it.hasNext) {
          rawResult += parseMap(it.next())
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

  def getByUsername(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()
      val label = DynamicLabel.label("NeoUser")

      // Gets nodes by uuid
      for (item <- args) {
        // Extracts result
        val username = item("username").asInstanceOf[String]
        val rawNode = graphDB.findNodesByLabelAndProperty(label, "username", username)

        val it = rawNode.iterator()
        if (it.hasNext) {
          rawResult += parseMap(it.next())
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

  def getByLabel(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()

      // Gets nodes by label
      for (item <- args) {
        val nodeWithOneLabel: ListBuffer[Map[String, Any]] = ListBuffer()

        // Extracts result
        val label = DynamicLabel.label(item("label").asInstanceOf[String])
        val rawNode = globalOperations.getAllNodesWithLabel(label)

        val it = rawNode.iterator()
        while (it.hasNext) {
          nodeWithOneLabel += parseMap(it.next())
        }
        it.close()

        rawResult += nodeWithOneLabel.toList
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
        rawResult += parseMap(it.next())
      }
      it.close()

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

        var childrenProps: Set[(String, Any)] = Set()
        var relProps: Set[(String, Any)] = Set()

        if (item("childrenProps") != null) {
          childrenProps = item("childrenProps")
            .asInstanceOf[Map[String, Any]]
            .toSet[(String, Any)]
        }

        if (item("relProps") != null) {
          relProps = item("relProps")
            .asInstanceOf[Map[String, Any]]
            .toSet[(String, Any)]
        }

        val limit = item("limit").asInstanceOf[Int]

        val it = rawParentNode.iterator()
        if (it.hasNext) {
          val childrenOfOneNode: ListBuffer[Map[String, Any]] = ListBuffer()
          val parentNode = it.next()

          // Gets all outgoing relationships of given type
          val relType = DynamicRelationshipType.withName(item("relType").asInstanceOf[String])
          val relList = parentNode.getRelationships(relType, Direction.OUTGOING).iterator()

          // Gets children and extracts partial result
          var count = 0
          while (relList.hasNext && (limit == 0 || (limit > 0 && count < limit))) {
            val rel = relList.next()
            val node = parseSet(rel.getEndNode)

            // TODO: make it more efficient
            if (childrenProps.subsetOf(node) && relProps.subsetOf(parseSet(rel))) {
              childrenOfOneNode += node.toMap[String, Any]
              count += 1
            }
          }

          rawResult += childrenOfOneNode.toList
        } else {
          rawResult += List()
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

        var childrenProps: Set[(String, Any)] = Set()
        var relProps: Set[(String, Any)] = Set()

        if (item("childrenProps") != null) {
          childrenProps = item("childrenProps")
            .asInstanceOf[Map[String, Any]]
            .toSet[(String, Any)]
        }

        if (item("relProps") != null) {
          relProps = item("relProps")
            .asInstanceOf[Map[String, Any]]
            .toSet[(String, Any)]
        }

        val limit = item("limit").asInstanceOf[Int]

        val it = rawParentNode.iterator()
        if (it.hasNext) {
          val instancesOfOneNode: ListBuffer[Map[String, Any]] = ListBuffer()
          val parentNode = it.next()

          // Gets all outgoing relationships of type <<INSTANCE>>
          val relType = DynamicRelationshipType.withName("<<INSTANCE>>")
          val relList = parentNode.getRelationships(relType, Direction.OUTGOING).iterator()

          // Gets children and extracts partial result
          var count = 0
          while (relList.hasNext && (limit == 0 || (limit > 0 && count < limit))) {
            val rel = relList.next()
            val node = parseSet(rel.getEndNode)

            // TODO: make it more efficient
            if (childrenProps.subsetOf(node) && relProps.subsetOf(parseSet(rel))) {
              instancesOfOneNode += node.toMap[String, Any]
              count += 1
            }
          }

          rawResult += instancesOfOneNode.toList
        } else {
          rawResult += List()
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

  def getUserFeeds(args: List[Map[String, Any]]): List[Any] = {
    var result: List[List[Map[String, Any]]] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[List[Map[String, Any]]] = ListBuffer()
      val userLabel = DynamicLabel.label("NeoUser")

      for (item <- args) {
        // Gets each user as an instance of Node
        val rawParentNode = graphDB.findNodesByLabelAndProperty(
          userLabel,
          "uuid",
          item("uuid").asInstanceOf[String]
        )

        val limit = item("limit").asInstanceOf[Int]

        val it = rawParentNode.iterator()
        if (it.hasNext) {
          val feedsOfOneNode: ListBuffer[Map[String, Any]] = ListBuffer()
          val user = it.next()

          // Gets all outgoing relationships of type <<FEED>>
          val relType = DynamicRelationshipType.withName("<<FEED>>")
          val relList = user.getRelationships(relType, Direction.OUTGOING).iterator()

          // Gets feeds and extracts partial result
          var count = 0
          while (relList.hasNext && (limit == 0 || (limit > 0 && count < limit))) {
            val rel = relList.next()
            val node = parseSet(rel.getEndNode)
            feedsOfOneNode += node.toMap[String, Any]
            count += 1
          }

          rawResult += feedsOfOneNode.toList
        } else {
          rawResult += List()
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

  def setLabel(args: List[Map[String, Any]]): List[Any] = {
    val tx = graphDB.beginTx()
    try {
      val nodeLabel = DynamicLabel.label("Node")

      for (item <- args) {
        // Gets each node as an instance of Node
        val rawNode = graphDB.findNodesByLabelAndProperty(
          nodeLabel,
          "uuid",
          item("uuid").asInstanceOf[String]
        )

        val it = rawNode.iterator()
        if (it.hasNext) {
          val node = it.next()

          // Sets label to the node
          val label = DynamicLabel.label(item("label").asInstanceOf[String])
          node.addLabel(label)
        }
        it.close()
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

  def deleteLabel(args: List[Map[String, Any]]): List[Any] = {
    val tx = graphDB.beginTx()
    try {
      val nodeLabel = DynamicLabel.label("Node")

      for (item <- args) {
        // Gets each node as an instance of Node
        val rawNode = graphDB.findNodesByLabelAndProperty(
          nodeLabel,
          "uuid",
          item("uuid").asInstanceOf[String]
        )

        val it = rawNode.iterator()
        if (it.hasNext) {
          val node = it.next()

          // Deletes label from the node
          val label = DynamicLabel.label(item("label").asInstanceOf[String])
          node.removeLabel(label)
        }
        it.close()
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
          it.close()
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
        val keys = item("propKeys").asInstanceOf[List[String]]

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
          it.close()
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

  def createModelNodes(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Map[String, Any]] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Map[String, Any]] = ListBuffer()
      val rootLabel = DynamicLabel.label("Root")

      // Gets raw root
      val rawRoot = globalOperations.getAllNodesWithLabel(rootLabel)

      // Extracts root
      var root: Node = null
      val it = rawRoot.iterator()
      if (it.hasNext) {
        root = it.next()
      } else {
        // TODO: for development purposes
        val nodeLabel = DynamicLabel.label("Node")
        root = graphDB.createNode(rootLabel, nodeLabel)
        root.setProperty("uuid", "root")
      }
      it.close()

      for (item <- args) {
        val modelName = item("modelName").asInstanceOf[String]
        val modelProps: Map[String, Any] = Map(
          "uuid" -> UUID.randomUUID().toString,
          "app_label" -> "rss",
          "name" -> ("rss:" + modelName),
          "model_name" -> modelName
        )

        val nodeLabel = DynamicLabel.label("Node")
        val modelLabel = DynamicLabel.label("Model")
        val modelNode = graphDB.createNode()
        modelNode.addLabel(nodeLabel)
        modelNode.addLabel(modelLabel)

        // Sets properties
        for ((key, value) <- modelProps) {
          modelNode.setProperty(key, value)
        }

        // Creates relationship from root
        val rel = DynamicRelationshipType.withName("<<TYPE>>")
        root.createRelationshipTo(modelNode, rel)

        rawResult += Map("uuid" -> modelProps("uuid"))
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

  // TODO: Add defaults
  def createNodes(args: List[Map[String, Any]]): List[Any] = {
    var result: List[Map[String, Any]] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Map[String, Any]] = ListBuffer()
      var modelNodes: Map[String, Node] = Map()

      // Simply gets model nodes
      val modelLabel = DynamicLabel.label("Model")
      val rawModelResult = globalOperations.getAllNodesWithLabel(modelLabel)

      // Saves model nodes
      val it = rawModelResult.iterator()
      while (it.hasNext) {
        val node = it.next()
        modelNodes += node.getProperty("model_name").asInstanceOf[String] -> node
      }
      it.close()

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

        val relType = item("type").asInstanceOf[String]

        val it1 = rawStartNode.iterator()
        val it2 = rawEndNode.iterator()
        if (it1.hasNext && it2.hasNext) {
          val startNode = it1.next()
          val endNode = it2.next()
          val dynamiceRelType = DynamicRelationshipType.withName(relType)

          // Creates a relationship of a given type
          val rel = startNode.createRelationshipTo(endNode, dynamiceRelType)

          // Sets properties to the relationship
          for ((key, value) <- item("props").asInstanceOf[Map[String, Any]]) {
            rel.setProperty(key, value)
          }
        }
        it1.close()
        it2.close()
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

  def createUniqueRelationships(args: List[Map[String, Any]]): List[Any] = {
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

        val relType = item("type").asInstanceOf[String]

        val it1 = rawStartNode.iterator()
        val it2 = rawEndNode.iterator()
        if (it1.hasNext && it2.hasNext) {
          val startNode = it1.next()
          val endNode = it2.next()
          val dynamiceRelType = DynamicRelationshipType.withName(relType)

          // Checks if the relationship is unique
          var isUnique = true
          val checkedRels = startNode.getRelationships(Direction.OUTGOING)
          val it3 = checkedRels.iterator()
          while (it3.hasNext) {
            val checkedRel = it3.next()
            if (checkedRel.getEndNode.getId == endNode.getId && checkedRel.getType.name() == relType) {
              isUnique = false
            }
          }

          if (isUnique) {
            // Creates a relationship of a given type
            val rel = startNode.createRelationshipTo(endNode, dynamiceRelType)

            // Sets properties to the relationship
            for ((key, value) <- item("props").asInstanceOf[Map[String, Any]]) {
              rel.setProperty(key, value)
            }
          }
        }
        it1.close()
        it2.close()
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
          var break = false
          while (!break && relList.hasNext) {
            val rel = relList.next()
            if (endNodeUuid == rel.getEndNode.getProperty("uuid").asInstanceOf[String]) {
              rel.delete()
              break = true
            }
          }
        }
        it.close()
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
          val props = item("props").asInstanceOf[Map[String, Any]]

          if (props != null) {
            // Looks through a list of relationships to delete a proper one
            val relList = startNode.getRelationships(Direction.OUTGOING).iterator()
            var break = false
            while (!break && relList.hasNext) {
              val rel = relList.next()
              if (endNodeUuid == rel.getEndNode.getProperty("uuid").asInstanceOf[String]) {
                // Sets properties to the relationship
                for ((key, value) <- props) {
                  rel.setProperty(key, value)
                }
                break = true
              }
            }
          }
        }
        it.close()
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
          val propKeys = item("propKeys").asInstanceOf[List[String]]

          if (propKeys != null) {
            // Looks through a list of relationships to delete a proper one
            val relList = startNode.getRelationships(Direction.OUTGOING).iterator()
            var break = false
            while (!break && relList.hasNext) {
              val rel = relList.next()
              if (endNodeUuid == rel.getEndNode.getProperty("uuid").asInstanceOf[String]) {
                // Delete relationship's properties
                for (key <- propKeys) {
                  rel.removeProperty(key)
                }
                break = true
              }
            }
          }
        }
        it.close()
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
