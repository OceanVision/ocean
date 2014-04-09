package text_processing

import edu.stanford.nlp.ie.crf.CRFClassifier
import scala.collection.mutable.ListBuffer
import scala.collection.mutable.ListBuffer
import scala.collection.JavaConversions._

class FourClassNERTagger extends NERTagger {

  // Load CRF Classifier from file, at this time 4 class classifier 
  val serializedClassifier = "stanford_classifiers/english.conll.4class.distsim.crf.ser.gz"
  val classifier = CRFClassifier.getClassifierNoExceptions(serializedClassifier)

  def tag(text: String): Seq[NERTag] = {

    val keywords = ListBuffer[(String, String)]()
    val tag_list = ListBuffer[NERTag]()

    val out = classifier.classifyWithInlineXML(text)

    val xml = scala.xml.XML.loadString("<s>" + out + "</s>")
    (xml \ "ORGANIZATION").foreach(org => keywords.add((org.text, "ORGANIZATION")))
    (xml \ "PERSON").foreach(per => keywords.add((per.text, "PERSON")))
    (xml \ "LOCATION").foreach(loc => keywords.add((loc.text, "LOCATION")))
    (xml \ "MISC").foreach(loc => keywords.add((loc.text, "MISC")))

    keywords.distinct.foreach(tag => tag_list.add(new NERTag(tag._1, tag._2)))

    tag_list.toSeq

  }
}