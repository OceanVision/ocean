lazy val stampleRootProject = Project(id = "mantis_shrimp",base = file("."))

name := "mantis_shrimp"

version := "1.0"

scalaVersion := "2.10.2"

resolvers += "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"

libraryDependencies += "com.typesafe.akka" % "akka-actor_2.10" % "2.2-M1" classifier "javadoc"

libraryDependencies += "com.typesafe.akka" % "akka-actor_2.10" % "2.2-M1"

libraryDependencies += "org.scala-sbt" % "sbt" % "0.13.1"

libraryDependencies += "org.apache.kafka" % "kafka_2.10" % "0.8.1"

libraryDependencies += "com.101tec" % "zkclient" % "0.3"

libraryDependencies += "log4j" % "log4j" % "1.2.17"

libraryDependencies += "net.sf.jopt-simple" % "jopt-simple" % "4.5"

libraryDependencies += "org.apache.avro" % "avro" % "1.7.5"

libraryDependencies += "com.github.scopt" % "scopt_2.9.2" % "3.1.0"

libraryDependencies +=  "com.yammer.metrics" % "metrics-core" % "2.2.0"

libraryDependencies +=  "nl.grons" % "metrics-scala_2.9.2" % "3.0.3"

libraryDependencies +=  "org.apache.thrift" % "libthrift" % "0.9.1"

libraryDependencies +=  "joda-time" % "joda-time" % "2.3"

libraryDependencies +=  "org.joda" % "joda-convert" % "1.5"

libraryDependencies +=  "org.specs2" % "specs2_2.10" % "2.2.2"

libraryDependencies ++= Seq("com.propensive" %% "rapture-core" % "0.9.0")

libraryDependencies ++= Seq("com.propensive" %% "rapture-json" % "0.9.1")

libraryDependencies ++= Seq("com.propensive" %% "rapture-io" % "0.9.1")

libraryDependencies ++= Seq("com.propensive" %% "rapture-io" % "0.9.1" classifier "javadoc")

libraryDependencies ++= Seq("com.propensive" %% "rapture-net" % "0.9.0")

libraryDependencies ++= Seq("com.propensive" %% "rapture-net" % "0.9.0" classifier "javadoc")

libraryDependencies ++= Seq("com.propensive" %% "rapture-fs" % "0.9.0")

libraryDependencies ++= Seq("com.propensive" %% "rapture-fs" % "0.9.0" classifier "javadoc")


