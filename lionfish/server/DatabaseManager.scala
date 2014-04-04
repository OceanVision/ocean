package lionfish
import java.util.UUID
import org.neo4j.graphdb.factory.GraphDatabaseFactory
import org.neo4j.graphdb._
import org.neo4j.cypher.{ExecutionEngine, ExecutionResult}
import org.neo4j.tooling.GlobalGraphOperations

// TODO: logging, nicer way of handling errors

class DatabaseManager {
  private val DB_PATH = "/usr/local/lib/neo4j/data/graph.db"
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
        println(s"Parsing node failed. Error message: $e")
      }
      null
    }
  }

  private def executeCypher(query: String, params: Map[String, Any] = Map()): List[List[Any]] = {
    try {
      cypherResult = cypherEngine.execute(query, params)
      var parsedResult: List[List[Any]] = List()
      for (row: Map[String, Any] <- cypherResult) {
        var rowItems: List[Any] = List()
        for (column <- row) {
          // TODO: Do not assume that every value is Node
          rowItems = rowItems :+ parseNode(column._2.asInstanceOf[Node])
        }
        parsedResult = parsedResult :+ rowItems
      }

      parsedResult
    } catch {
      case e: Exception => {
        println(s"Executing Cypher failed. Error message: $e")
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
        println(s"Initialising cache failed. Error message: $e")
      }
    }
  }

  def getModelNodes(): List[Any] = {
    var result: List[Any] = List()

    val tx = graphDB.beginTx()
    try {
      // Simply gets model nodes
      val rawResult = globalOperations.getAllNodesWithLabel(DynamicLabel.label("Model"))
      tx.success()

      // Extracts result
      val it = rawResult.iterator()
      while (it.hasNext) {
        result = result :+ parseNode(it.next())
      }
      it.close()
    } catch {
      case e: Exception => {
        println(s"Executing function failed. Error message: $e")
      }
      result = List()
    } finally {
      tx.close()
    }

    result
  }

  // TODO: Add defaults
  def createNodes(nodeParamsList: List[Map[String, Any]]): List[Any] = {
    var result: List[String] = List()

    val tx = graphDB.beginTx()
    try {
      // Creates nodes by the given properties
      for (params <- nodeParamsList) {
        val uuid = UUID.randomUUID().toString
        var props = params("props").asInstanceOf[Map[String, Any]]
        props += "uuid" -> uuid
        result = result :+ uuid

        val node = graphDB.createNode()
        for ((key, value) <- props) {
          node.setProperty(key, value)
        }

        val modelName = params("modelName").asInstanceOf[String]
        node.addLabel(DynamicLabel.label(modelName))

        val relType = DynamicRelationshipType.withName(params("relType").asInstanceOf[String])
        modelNodes(modelName).createRelationshipTo(node, relType)
      }
      tx.success()
    } catch {
      case e: Exception => {
        println(s"Executing function failed. Error message: $e")
      }
      result = List()
    } finally {
      tx.close()
    }

    result
  }

  def deleteNodes(nodeParamsList: List[Map[String, Any]]): List[Any] = {
    // Prepares params
    var nodeUuidList: List[String] = List()
    for (item <- nodeParamsList) {
      nodeUuidList = nodeUuidList :+ item("uuid").asInstanceOf[String]
    }

    val tx = graphDB.beginTx()
    try {
      // Builds query and executes
      val query =
        "MATCH (e:Node)-[r]-() " +
        "USING INDEX e:Node(uuid) " +
        "WHERE e.uuid IN {uuid_list} " +
        "DELETE e, r"
      executeCypher(query, Map("uuid_list" -> nodeUuidList))
      tx.success()
    } catch {
      case e: Exception => {
        println(s"Executing function failed. Error message: $e")
      }
    } finally {
      tx.close()
    }

    null
  }
}
