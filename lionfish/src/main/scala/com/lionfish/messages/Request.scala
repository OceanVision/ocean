package com.lionfish.messages

case class Request(connectionUuid: String, request: Map[String, Any]) extends Message
