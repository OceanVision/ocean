Read wiki Deployment Installation -> Scala page

Make sure sbt is above 13.0 (`sbt --version`). SBT installation is easy - follow
setup documentation on scala-sbt

Run

`sbt update`

`sbt gen-idea`

And open project in IntelliJ (remember to see project structure if is correct -
ctrl+alt+shift+s)


**Note**

In case of problems try compiling kafka from github repository
and add it to lib/ directory

Also Kafka sometimes is failing LeaderElection

