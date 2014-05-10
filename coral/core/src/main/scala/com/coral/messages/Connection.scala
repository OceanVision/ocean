package com.coral.messages

import java.net.Socket

case class Connection(id: Int, socket: Socket) extends Message
