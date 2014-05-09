package com.lionfish.server

object Launcher {
  def main(args: Array[String]) = {
    new Thread(Server).start()
  }
}
