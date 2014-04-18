/**
 * Created by staszek on 4/18/14.
 */

// See https://github.com/propensive/rapture-json-test/blob/master/src/json.scala - for scala test of json

package mantis_shrimp
import rapture.core._
import rapture.json._
import jsonParsers.scalaJson._
import scala.util.parsing.json._

//Internal strategy for Rapture.io - I dont see this design choice..
import strategy.throwExceptions

object Sandbox extends App {
   def runTest(implicit parser: JsonBufferParser[String]){

     val json_example = json""" {"ala":13, "beka":[1,2,"ala2"]} """

     println(json_example) ;

     println(json_example.ala.as[Int]);
   }

  runTest
}
