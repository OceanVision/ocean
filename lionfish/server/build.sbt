scalaHome := Some(file("/usr/lib/scala"))

mainClass in (Compile, run) := Some("lionfish.Server")
