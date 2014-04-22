package lionfish.client

trait Method {
  protected def method(getOnlyRequest: Boolean = false): Any

  def run(): Any = {
    method()
  }

  def getRequest: Any = {
    method(getOnlyRequest = true)
  }
}
