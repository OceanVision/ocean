name := "lionfish"

version := "0.9"

scalaVersion := "2.10.4"

mainClass in (Compile, run) := Some("com.lionfish.server.Launcher")

libraryDependencies += "org.neo4j" % "neo4j" % "2.0.2"

libraryDependencies ++= Seq("com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.3.3")

libraryDependencies += "org.scalatest" % "scalatest_2.10" % "2.1.4" % "test"
