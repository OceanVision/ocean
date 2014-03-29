scalaHome := Some(file("/usr/lib/scala"))

mainClass in (Compile,run) := Some("lionfish.Server")

resolvers += "repo.codahale.com" at "http://repo.codahale.com"

libraryDependencies += "com.codahale" % "jerkson_2.9.1" % "0.5.0"