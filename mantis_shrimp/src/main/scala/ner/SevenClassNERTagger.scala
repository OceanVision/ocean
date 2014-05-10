package ner

import edu.stanford.nlp.ie.crf.CRFClassifier
import scala.collection.mutable.ListBuffer
import scala.collection.JavaConversions._
import mantisshrimp.MantisTag

class SevenClassNERTagger extends NERTagger {

  // Load CRF Classifier from file, at this time 4 class classifier 
  val serializedClassifier = "stanford_classifiers/english.muc.7class.distsim.crf.ser.gz"
  val classifier = CRFClassifier.getClassifierNoExceptions(serializedClassifier)

  def tag(text: String): Seq[MantisTag] = {
    val keywords = ListBuffer[(String, String)]()
    val tag_list = ListBuffer[MantisTag]()

    val out = classifier.classifyWithInlineXML(scala.xml.Utility.escape(text))

    try{
      val xml = scala.xml.XML.loadString("<s>" + out + "</s>")
      (xml \ "ORGANIZATION").foreach(org => keywords.add((org.text, "ORGANIZATION")))
      (xml \ "PERSON").foreach(per => keywords.add((per.text, "PERSON")))
      (xml \ "LOCATION").foreach(loc => keywords.add((loc.text, "LOCATION")))
      (xml \ "TIME").foreach(loc => keywords.add((loc.text, "TIME")))
      (xml \ "MONEY").foreach(loc => keywords.add((loc.text, "MONEY")))
      (xml \ "DATE").foreach(loc => keywords.add((loc.text, "DATE")))
      (xml \ "PERCENT").foreach(loc => keywords.add((loc.text, "PERCENT")))

      keywords.distinct.foreach(tag => tag_list.add(new MantisTag(tag._1, tag._2)))
    }
    catch{
      case e: Exception =>{
        println("Failed parsing XML out of Stanford")
        println("Input text "+text)
        println(out.toString)
        println("Error "+e.toString)

      }
    }

    tag_list.toSeq

  }
}

