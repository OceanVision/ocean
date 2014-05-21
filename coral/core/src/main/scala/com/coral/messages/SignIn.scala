package com.coral.messages

case class SignIn(clientUuid: String, userUuid: String) extends Message
