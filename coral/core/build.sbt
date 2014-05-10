name := "coral-core"

version := "0.9"

scalaVersion := "2.10.4"

mainClass in (Compile, run) := Some("com.coral.connector.Launcher")

resolvers += "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"

libraryDependencies ++= Seq("com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.3.3")

libraryDependencies ++= Seq(
  "com.typesafe.akka" %% "akka-actor"   % "2.3.2",
  "com.typesafe.akka" %% "akka-remote"  % "2.3.2"
)
