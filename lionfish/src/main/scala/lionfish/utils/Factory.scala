package lionfish.utils
import lionfish.client.Batch

trait Factory {
  def getBatch: Batch
}
