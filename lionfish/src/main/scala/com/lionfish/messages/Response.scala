package com.lionfish.messages

case class Response(clientUuid: String, request: Request, result: Any) extends Message
