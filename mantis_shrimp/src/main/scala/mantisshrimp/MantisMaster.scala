package mantisshrimp
import akka.actor.Actor._

/**
 * Created by staszek on 5/16/14.
 */
class MantisMaster {
  var hasTagger = false
  var hasNewsFetcher = false
  var hasNeo4jDumper = false



  def receive = {
    case Tag(x) => {

    }
    case GetType => {

    }

  }
}
