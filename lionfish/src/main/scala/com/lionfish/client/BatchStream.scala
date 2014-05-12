package com.lionfish.client

class BatchStream extends Stream {
  override def !!(method: Method): Any = {
    method.executeBatch()
  }

  override def execute(): Any = {
    val result = macroMethod.executeBatch()
    macroMethod = null
    result
  }
}
