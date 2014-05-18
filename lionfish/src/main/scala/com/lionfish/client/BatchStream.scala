package com.lionfish.client

class BatchStream(
  protected val serverAddress: String,
  protected val serverPort: Int) extends Stream {

  override def !!(method: Method): Any = {
    method.executeBatch()
  }

  override def execute(): Any = {
    val result = macroMethod.executeBatch()
    macroMethod = null
    result
  }
}
