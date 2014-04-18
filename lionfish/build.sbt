scalaVersion := "2.10.4"

mainClass in (Compile, run) := Some("lionfish.server.Server")

libraryDependencies += "org.neo4j" % "neo4j" % "2.0.2"

libraryDependencies ++= Seq("com.propensive" %% "rapture-core" % "0.9.0")

libraryDependencies ++= Seq("com.propensive" %% "rapture-json" % "0.9.1")
