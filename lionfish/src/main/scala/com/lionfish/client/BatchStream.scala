package com.lionfish.client

import akka.actor.ActorSystem

class BatchStream(
  protected val streamSystem: ActorSystem,
  protected val proxyAddress: String,
  protected val proxyPort: Int) extends Stream {

  override def !!(method: Method): Any = {
    method.executeBatch()
  }

  override def execute(): Any = {
    val result = macroMethod.executeBatch()
    macroMethod = null
    result
  }
}
