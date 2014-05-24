package com.lionfish.logging

object Logging {
  private val errorMask = 1
  private val infoMask = 3
  private val debugMask = 5

  // Chain of responsibility
  private val logger: Logger = new DebugLogger
  logger.setNext(new InfoLogger).setNext(new ErrorLogger)

  def error(message: String) = {
    logger.log(errorMask, message)
  }

  def info(message: String) = {
    logger.log(infoMask, message)
  }

  def debug(message: String) = {
    logger.log(debugMask, message)
  }
}
