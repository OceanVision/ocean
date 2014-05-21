package com.lionfish.client

class SequenceStream(
  protected val serverAddress: String,
  protected val serverPort: Int) extends Stream {

  override def !!(method: Method): Any = {
    method.executeSequence()
  }

  override def execute(): Any = {
    val result = macroMethod.executeSequence()
    macroMethod = null
    result
  }
}
