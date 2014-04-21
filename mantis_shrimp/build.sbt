lazy val stampleRootProject = Project(id = "mantis_shrimp",base = file("."))

name := "mantis_shrimp"

version := "1.0"

scalaVersion := "2.10.2"

resolvers += "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"

libraryDependencies += "org.apache.kafka" % "kafka_2.10" % "0.8.1"

libraryDependencies += "org.monifu" %% "monifu-core" % "0.5"

libraryDependencies += "com.typesafe.akka" % "akka-actor_2.10" % "2.2-M1"

libraryDependencies += "org.scala-sbt" % "sbt" % "0.13.1"

libraryDependencies += "log4j" % "log4j" % "1.2.17"

libraryDependencies ++= Seq("com.propensive" %% "rapture-core" % "0.9.0")

libraryDependencies ++= Seq("com.propensive" %% "rapture-json" % "0.9.1")

libraryDependencies ++= Seq("com.propensive" %% "rapture-io" % "0.9.1")

libraryDependencies ++= Seq("com.propensive" %% "rapture-io" % "0.9.1" classifier "javadoc")

libraryDependencies ++= Seq("com.propensive" %% "rapture-net" % "0.9.0")

libraryDependencies ++= Seq("com.propensive" %% "rapture-net" % "0.9.0" classifier "javadoc")

libraryDependencies ++= Seq("com.propensive" %% "rapture-fs" % "0.9.0")

libraryDependencies ++= Seq("com.propensive" %% "rapture-fs" % "0.9.0" classifier "javadoc")

