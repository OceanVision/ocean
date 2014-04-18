/**
 * Created by staszek on 4/18/14.
 */

package mantis_shrimp
import rapture.core._
import rapture.json._
import rapture.io._
import rapture.net._

//Internal strategy for Rapture.io - I dont see this design choice..
import strategy.throwExceptions


object DonCorleoneUtils extends App {
  implicit val enc = Encodings.`UTF-8`
  val txt = (Http / "rapture.io" / "welcome.txt").slurp[Char]
  println(txt)


}
