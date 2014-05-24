package com.lionfish.logging

class InfoLogger extends Logger {
  private val mask = 3
  private val prefix = Console.YELLOW + "[INFO] " + Console.RESET

  override def log(level: Int, message: String) = {
    if (level == mask) {
      println(prefix + message)
    } else if (next != null) {
      next.log(level, message)
    }
  }
}
