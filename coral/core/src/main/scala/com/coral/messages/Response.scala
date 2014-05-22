package com.coral.messages

case class Response(uuid: String, request: Map[String, Any], result: Any) extends Message
