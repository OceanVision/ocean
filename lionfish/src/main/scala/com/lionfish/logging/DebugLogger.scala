package com.lionfish.logging

class DebugLogger extends Logger {
  private val mask = 5
  private val prefix = Console.CYAN + "[DEBUG] " + Console.RESET

  override def log(level: Int, message: String) = {
    if (level == mask) {
      println(prefix + message)
    } else if (next != null) {
      next.log(level, message)
    }
  }
}
