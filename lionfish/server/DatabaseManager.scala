package lionfish
import org.neo4j.graphdb.factory._
import org.neo4j.graphdb._
import org.neo4j.cypher._

// TODO: logging, nicer way of handling errors

class DatabaseManager {
  private val DB_PATH = "/usr/local/lib/neo4j/data/graph.db"
  private val graphDB = new GraphDatabaseFactory().newEmbeddedDatabase(DB_PATH)

  private val cypherEngine = new ExecutionEngine(graphDB)
  private var cypherResult: ExecutionResult = null

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

  private def executeCypher(query: String): List[List[Any]] = {
    try {
      cypherResult = cypherEngine.execute(query)
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

  def getModelNodes(): List[Any] = {
    try {
      // Builds query and executes
      val tx = graphDB.beginTx()
      val query =
        "MATCH (e:Model)\n" +
        "RETURN e"
      val rawResult = executeCypher(query)
      tx.success()

      // Extracts result
      var result: List[Any] = List()
      for (item <- rawResult) {
        result = result :+ item(0)
      }

      result
    } catch {
      case e: Exception => {
        println(s"Executing function failed. Error message: $e")
      }
      List()
    }
  }
}
