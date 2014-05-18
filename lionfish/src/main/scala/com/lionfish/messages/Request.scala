package com.lionfish.messages

case class Request(clientUuid: String, request: Map[String, Any]) extends Message
