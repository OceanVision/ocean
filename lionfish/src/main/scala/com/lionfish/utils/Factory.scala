package com.lionfish.utils

import com.lionfish.client.Batch

trait Factory {
  def getBatch: Batch
}
