resolvers += "Sonatype snapshots" at "https://oss.sonatype.org/content/repositories/snapshots/"

addSbtPlugin("com.github.mpeltonen" % "sbt-idea" % "1.7.0-SNAPSHOT")

addSbtPlugin("org.scala-sbt.plugins" % "sbt-onejar" % "0.8")

addSbtPlugin("net.virtual-void" % "sbt-dependency-graph" % "0.7.4")

logLevel := Level.Warn
