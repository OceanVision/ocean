Read wiki Deployment Installation -> Scala page


**Opening in IntelliJ**

Run

`sbt update`

`sbt gen-idea`

And open project in IntelliJ (remember to see project structure if is correct -
ctrl+alt+shift+s).

You will need to add manually following libraries (sbt gen-idea plugin bug):

com.typesafe.akka.akka_remote == 2.3.1
com.typesafe.akka.akka_actor == 2.3.1
com.typesafe.config == 2.2.1

**Dependencies**

Make sure sbt is above 13.0 (`sbt --version`). SBT installation is easy - follow
setup documentation on scala-sbt

1. Download following libraries and put them in lib folder:

  * stanford-ner : http://nlp.stanford.edu/software/CRF-NER.shtml - put .jars in lib/

2. Download http://nlp.stanford.edu/software/CRF-NER.shtml and
put stanford_classifiers (trained classifiers) folder in mantis_shrimp/ folder

3. Run `sbt update`

**Running project**

Type `sbt run`

To run with parameters : `sbt "run --param 1 --param 2"`

Example : `sbt "run --port 2553 --config_path mantis_slave.conf"`


**Note**

In case of problems try compiling kafka from github repository
and add it to lib/ directory

Also Kafka sometimes is failing LeaderElection

