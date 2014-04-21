package lionfish.utils
import java.lang.reflect.{Type, ParameterizedType}
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule
import com.fasterxml.jackson.core.`type`.TypeReference

object json {
  private val jsonMapper = new ObjectMapper()
  jsonMapper.registerModule(DefaultScalaModule)

  private [this] def typeReference[T: Manifest] = new TypeReference[T] {
    override def getType = typeFromManifest(manifest[T])
  }

  private [this] def typeFromManifest(m: Manifest[_]): Type = {
    if (m.typeArguments.isEmpty) { m.erasure }
    else new ParameterizedType {
      def getRawType = m.erasure
      def getActualTypeArguments = m.typeArguments.map(typeFromManifest).toArray
      def getOwnerType = null
    }
  }

  def serialise(rawData: Any): String = {
    import java.io.StringWriter
    val writer = new StringWriter()
    jsonMapper.writeValue(writer, rawData)
    writer.toString
  }

  def deserialise[T: Manifest](rawData: String) : T = {
    jsonMapper.readValue[T](rawData, typeReference[T])
  }
}
