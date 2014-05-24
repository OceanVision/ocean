package com.lionfish.client

class SequenceStream(
  protected val serverAddress: String,
  protected val serverPort: Int) extends Stream {

  override def !!(method: Method): Any = {
    method.executeSequence()
  }

  override def execute(): Any = {
    var result: List[Any] = null

    try {
      result = macroMethod.executeSequence()
      macroMethod = null
    } catch {
      case e: Exception => {
        log.error(s"Failed to execute the sequence.")
      }
    }

    result
  }
}
