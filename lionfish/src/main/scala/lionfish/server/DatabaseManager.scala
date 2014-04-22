package lionfish.server
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

  private def parseNode(node: Node): Map[String, Any] = {
    try {
      val keys = node.getPropertyKeys
      var dict: Map[String, Any] = Map()
      val it = keys.iterator()
      while (it.hasNext) {
        val key = it.next()
        dict += key -> node.getProperty(key)
      }
      dict
    } catch {
      case e: Exception => {
        val line = e.getStackTrace()(2).getLineNumber
        println(s"Parsing node failed at line $line. Error message: $e")
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
          rowItems += parseNode(column._2.asInstanceOf[Node])
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

  def getByUuid(nodeUuidList: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()

      // Gets nodes by uuid
      for (item <- nodeUuidList) {
        // Extracts result
        val rawNode = graphDB.findNodesByLabelAndProperty(
          DynamicLabel.label("Node"),
          "uuid",
          item("uuid")
        )
        val it = rawNode.iterator()
        if (it.hasNext) {
          rawResult += parseNode(it.next())
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

  def getByLink(nodeUuidList: List[Map[String, Any]]): List[Any] = {
    var result: List[Any] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Any] = ListBuffer()

      // Gets nodes by uuid
      for (item <- nodeUuidList) {
        // Extracts result
        val rawNode = graphDB.findNodesByLabelAndProperty(
          DynamicLabel.label(item("modelName").asInstanceOf[String]),
          "link",
          item("link")
        )
        val it = rawNode.iterator()
        if (it.hasNext) {
          while (it.hasNext) {
            val node = parseNode(it.next())
            rawResult += node
          }
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

  def getModelNodes(requests: List[Map[String, Any]]): List[Any] = {
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
        rawResult += parseNode(it.next())
      }
      it.close()

      result = List.fill[Any](requests.length)(rawResult.toList)
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
  def createNodes(nodeParamsList: List[Map[String, Any]]): List[Any] = {
    var result: List[Map[String, Any]] = null

    val tx = graphDB.beginTx()
    try {
      val rawResult: ListBuffer[Map[String, Any]] = ListBuffer()

      // Creates nodes by the given properties
      for (params <- nodeParamsList) {
        val uuid = UUID.randomUUID().toString
        var props = params("props").asInstanceOf[Map[String, Any]]
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

  def deleteNodes(nodeParamsList: List[Map[String, Any]]): List[Any] = {
    // Prepares params
    var nodeUuidList: ListBuffer[String] = ListBuffer()
    for (item <- nodeParamsList) {
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
}
