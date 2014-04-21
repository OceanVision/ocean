package ner
import edu.stanford.nlp.ie.crf.CRFClassifier

trait NERTagger {

  val serializedClassifier: String
  val classifier : CRFClassifier[edu.stanford.nlp.ling.CoreLabel]

  def tag(text: String): Seq[NERTag]
}