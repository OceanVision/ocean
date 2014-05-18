name := "lionfish"

version := "0.9.3"

scalaVersion := "2.10.2"

javacOptions ++= Seq("-source", "1.7")

mainClass in (Compile, run) := Some("com.lionfish.server.Launcher")

resolvers += "Typesafe Repository" at "http://repo.typesafe.com/typesafe/releases/"

/** Repos for Neo4j Admin server dep */
resolvers ++= Seq(
  "tinkerprop" at "http://tinkerpop.com/maven2",
  "neo4j-public-repository" at "http://m2.neo4j.org/releases"
)

//libraryDependencies += "org.mortbay.jetty" % "jetty" % "6.1.14"
//
//libraryDependencies += "org.mortbay.jetty" % "jetty-util" % "6.1.14"
//
//libraryDependencies += "org.mortbay.jetty" % "servlet-api-2.5" % "6.1.5"
//
//libraryDependencies += "org.mortbay.jetty" % "jsp-2.1" % "6.1.11"
//
//libraryDependencies += "org.apache.tomcat" % "tomcat-servlet-api" % "7.0.47"

libraryDependencies += "com.sun.jersey" % "jersey-server" % "1.18.1"

libraryDependencies += "com.sun.jersey" % "jersey-core" % "1.18.1"

libraryDependencies += "com.sun.jersey" % "jersey-json" % "1.18.1"

libraryDependencies += "com.sun.jersey" % "jersey-servlet" % "1.18.1"

//libraryDependencies += "org.eclipse.jetty" % "jetty-server" % "9.2.0.M1"

libraryDependencies += "org.neo4j" % "neo4j" % "2.0.3"

libraryDependencies += "org.neo4j" % "neo4j-kernel" % "2.0.3"

libraryDependencies += "org.neo4j.app" % "neo4j-server" % "2.0.3" classifier "static-web"

//libraryDependencies += "commons-beanutils" % "commons-beanutils" % "1.8.2"
//
//libraryDependencies += "commons-beanutils" % "commons-beanutils-core" % "1.8.0"

libraryDependencies ++= Seq(
  "org.neo4j.app" % "neo4j-server" % "2.0.2"
)

libraryDependencies ++= Seq("com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.3.3")

libraryDependencies ++= Seq(
  "com.typesafe.akka" %% "akka-actor" % "2.3.2",
  "com.typesafe.akka" %% "akka-remote" % "2.3.2"
)

libraryDependencies += "org.scalatest" % "scalatest_2.10" % "2.1.4" % "test"
