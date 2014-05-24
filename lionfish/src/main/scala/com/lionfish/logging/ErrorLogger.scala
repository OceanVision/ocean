package com.lionfish.logging

class ErrorLogger extends Logger {
  private val mask = 1
  private val prefix = Console.BOLD + Console.RED + "[ERROR] " + Console.RESET

  override def log(level: Int, message: String) = {
    if (level == mask) {
      println(prefix + message)
    } else if (next != null) {
      next.log(level, message)
    }
  }
}
