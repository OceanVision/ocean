package com.lionfish.messages

case class Response(clientUuid: String, result: Any) extends Message
