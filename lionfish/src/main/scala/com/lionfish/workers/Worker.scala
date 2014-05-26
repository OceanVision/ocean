package com.lionfish.workers

import com.lionfish.messages.Request

trait Worker {
  def processRequest(request: Request): Any
}
