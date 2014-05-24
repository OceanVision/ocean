package com.lionfish.logging

trait Logger {
  protected var next: Logger = null

  def setNext(logger: Logger): Logger = {
    next = logger
    logger
  }

  def log(level: Int, message: String)
}
