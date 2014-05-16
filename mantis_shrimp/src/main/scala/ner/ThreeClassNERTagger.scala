package ner

import edu.stanford.nlp.ie.crf.CRFClassifier
import edu.stanford.nlp.ling.CoreAnnotations
import edu.stanford.nlp.ling.CoreLabel
import scala.collection.mutable.ListBuffer
import scala.collection.JavaConversions._
import mantisshrimp.MantisTag

class ThreeClassNERTagger extends NERTagger {

  // Load CRF Classifier from file, at this time 3 class classifier 
  val serializedClassifier = "stanford_classifiers/english.all.3class.distsim.crf.ser.gz"
  val classifier = CRFClassifier.getClassifierNoExceptions(serializedClassifier)

  override def tag(text: String): Seq[MantisTag] = {

    val keywords = ListBuffer[(String, String)]()
    val tag_list = ListBuffer[MantisTag]()

    val out = classifier.classifyWithInlineXML(text)

    val xml = scala.xml.XML.loadString("<s>" + out + "</s>")
    (xml \ "ORGANIZATION").foreach(org => keywords.add((org.text, "ORGANIZATION")))
    (xml \ "PERSON").foreach(per => keywords.add((per.text, "PERSON")))
    (xml \ "LOCATION").foreach(loc => keywords.add((loc.text, "LOCATION")))

    keywords.distinct.foreach(tag => tag_list.add(new MantisTag(tag._1, tag._2)))

    tag_list.toSeq

  }
}