/**
 * Created by staszek on 4/18/14.
 */

package mantisshrimp

import rapture.fs._
import rapture.io._
import rapture.net._
import rapture.core._
import rapture.json._
import jsonParsers.scalaJson._

//SBT configuration to retrieve settings - for instance base directory
//Unfortunately I do not know how to get it to work (2h research..)

//Internal strategy for Rapture.io - I dont see this design choice..
import strategy.throwExceptions


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
//  def get_configuration[T](service_name:String, config_name: String)(implicit m: scala.reflect.Manifest[T]): T={
//    val request_url = "get_configuration?service_name="+service_name+"&config_name="+config_name+"&node_id="+this.config.node_id.as[String]
//    println("Connecting to "+(this.don_url.replaceAll("http://","") / request_url).toString())
//    val value = JsonBuffer.parse((Http / this.don_url.replace("http://", "") / request_url).slurp[Char]).result
//    println(value.toString())
//    return value.toString().asInstanceOf[T]
//  }
  //TODO: why reflection fails sometimes?
  def get_configuration_string(service_name:String, config_name: String): String = {
    val request_url = "get_configuration?service_name="+service_name+"&config_name="+config_name+"&node_id="+this.config.node_id.as[String]
    println("Connecting to "+(this.don_url.replaceAll("http://","") / request_url).toString())
    val value = JsonBuffer.parse((Http / this.don_url.replace("http://", "") / request_url).slurp[Char]).result
    return value.toString()
  }

//  //Demo functions: TODO: convert to tests
//  println(get_configuration[String]("kafka","port"))
//  val txt = (Http / "rapture.io" / "welcome.txt").slurp[Char]
}
