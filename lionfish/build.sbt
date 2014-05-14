name := "lionfish"

version := "0.9.1"

scalaVersion := "2.10.4"

mainClass in (Compile, run) := Some("com.lionfish.server.Launcher")

resolvers += "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"

libraryDependencies += "org.neo4j" % "neo4j" % "2.0.2"

libraryDependencies ++= Seq(
  "com.typesafe.akka" %% "akka-actor" % "2.3.2",
  "com.typesafe.akka" %% "akka-remote" % "2.3.2"
)

libraryDependencies += "org.scalatest" % "scalatest_2.10" % "2.1.4" % "test"
