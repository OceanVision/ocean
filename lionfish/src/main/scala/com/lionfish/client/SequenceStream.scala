package com.lionfish.client

import akka.actor.ActorSystem

class SequenceStream(
  protected val streamSystem: ActorSystem,
  protected val proxyAddress: String,
  protected val proxyPort: Int) extends Stream {

  override def !!(method: Method): Any = {
    val result = method.executeSequence().asInstanceOf[List[Any]]

    if (result != null && result.length == 1) {
      result(0)
    } else {
      result
    }
  }

  override def execute(): Any = {
    val result = macroMethod.executeSequence().asInstanceOf[List[Any]]
    macroMethod = null

    if (result != null && result.length == 1) {
      result(0)
    } else {
      result
    }
  }
}
