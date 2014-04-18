package text_processing

class NERTag(_tag: String, _label: String) {

  val tag: String = _tag
  val desc: String = ""
  val label: String = _label	// ORGANIZATION, PERSON, LOCATION

  override def toString(): String = tag + " (" + label + ")"

}
  
