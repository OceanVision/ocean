/**
 * Created by staszek on 4/18/14.
 */

package mantis_shrimp
import rapture.fs._
import rapture.io._
import rapture.net._
import rapture.core._
import rapture.json._
import jsonParsers.scalaJson._

//SBT configuration to retrieve settings - for instance base directory
//Unfortunately I do not know how to get it to work (2h research..)
import sbt._

//Internal strategy for Rapture.io - I dont see this design choice..
import strategy.throwExceptions

import scala.reflect.Manifest
import scala.reflect.ClassTag

object DonCorleoneUtils{
  implicit val enc = Encodings.`UTF-8`
  //Not beautiful but works
  val mantis_shrimp_dir = new java.io.File(".").getCanonicalPath
  val config = JsonBuffer.parse((File / mantis_shrimp_dir / "../don_corleone" / "config.json").slurp[Char])
  val don_url: String = if (config.master_local.as[Boolean]) config.master_local.as[String] else config.master.as[String]

  /*
  * @returns Configuration of service
  * @note Abridged and simplified version of get_configuration from don_utils.py
   *
   */
  def get_configuration[T](service_name:String, config_name: String)(implicit m: scala.reflect.Manifest[T]): T={
    val request_url = "get_configuration?service_name="+service_name+"&config_name="+config_name+"&node_id="+this.config.node_id.as[String]
    println("Connecting to "+(this.don_url.replaceAll("http://","") / request_url).toString())
    val value = JsonBuffer.parse((Http / this.don_url.replace("http://", "") / request_url).slurp[Char]).result
    return value.asInstanceOf[T]
  }

  //Demo functions: TODO: convert to tests
  println(get_configuration[String]("kafka","port"))
  val txt = (Http / "rapture.io" / "welcome.txt").slurp[Char]
}
