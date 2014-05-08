package com.coral.connector

object Launcher {
  def main(args: Array[String]) = {
    new Thread(WebserviceConnector).start()
  }
}
