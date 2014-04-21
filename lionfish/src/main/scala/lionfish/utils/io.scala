package lionfish.utils
import java.net.Socket
import java.nio.ByteBuffer

object io {
  // Sends a message to socket
  def send(rawData: Any)(implicit socket: Socket) = {
    try {
      val outputStream = socket.getOutputStream

      // Serializes the data
      val serialisedMsg = json.serialise(rawData)

      // Prepares length of a outcoming array
      val byteBuffer = ByteBuffer.allocate(4)
      byteBuffer.putInt(serialisedMsg.length)
      val msgLength = byteBuffer.array()

      // Prepares a certain message
      val msg: Array[Byte] = msgLength ++ serialisedMsg.getBytes
      outputStream.write(msg)
    } catch {
      case e: Exception => {
        println(s"Failed to send data. Error message: $e")
      }
    }
  }

  // Receives a message from socket
  def receive[T: Manifest]()(implicit socket: Socket): T = {
    try {
      val inputStream = socket.getInputStream

      // Gets length of a incoming message
      var readBuffer = new Array[Byte](4)
      var count = inputStream.read(readBuffer, 0, 4)

      if (count == -1) {
        return null.asInstanceOf[T]
      }

      val dataLength: Int = ByteBuffer.wrap(readBuffer).getInt
      var msg: String = ""

      // Gets a certain message
      readBuffer = new Array[Byte](dataLength)
      var totalCount = 0
      count = 0
      while (totalCount < dataLength) {
        count = inputStream.read(readBuffer, 0, dataLength)
        totalCount += count
        msg += new String(readBuffer, 0, count)
      }

      // Parses msg to data
      json.deserialise[T](msg)
    } catch {
      case e: Exception => {
        println(s"Failed to receive data. Error message: $e")
      }
        null.asInstanceOf[T]
    }
  }
}
