package mantisshrimp

import ner.SevenClassNERTagger


class Mantis7ClassNERTagger(config: Map[String, String]) extends MantisTagger {
   val parentMantisPath = config(MantisLiterals.ParentMantisPath)

   val nerTagger = new SevenClassNERTagger()

   override def tag(x: scala.collection.mutable.Map[String, AnyRef]): Tuple2[String, Seq[MantisTag]] = {
     return (x("uuid").asInstanceOf[String], nerTagger.tag(x(MantisLiterals.ItemTitle)+" "+
       x(MantisLiterals.ItemText)+ " "+x(MantisLiterals.ItemSummary)))
   }
}

