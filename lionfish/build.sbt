scalaVersion := "2.10.4"

mainClass in (Compile, run) := Some("lionfish.server.Server")

resolvers += "spray" at "http://repo.spray.io/"

libraryDependencies += "org.neo4j" % "neo4j" % "2.0.2"

libraryDependencies ++= Seq("com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.3.3")
