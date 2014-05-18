package com.lionfish.client

trait Factory {
  def getBatchStream: Stream
  def getSequenceStream: Stream
}
