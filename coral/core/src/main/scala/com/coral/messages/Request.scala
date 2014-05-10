package com.coral.messages

case class Request(uuid: String, request: Map[String, Any]) extends Message
