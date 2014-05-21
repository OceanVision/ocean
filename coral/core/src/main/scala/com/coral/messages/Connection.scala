package com.coral.messages

import java.net.Socket

case class Connection(socket: Socket) extends Message
