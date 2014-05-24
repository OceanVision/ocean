package com.lionfish.client

class BatchStream(
  protected val serverAddress: String,
  protected val serverPort: Int) extends Stream {

  override def !!(method: Method): Any = {
    method.executeBatch()
  }

  override def execute(): Any = {
    var result: List[Any] = null

    try {
      result = macroMethod.executeBatch()
      macroMethod = null
    } catch {
      case e: Exception => {
        log.error(s"Failed to execute the batch.")
      }
    }

    result
  }
}
