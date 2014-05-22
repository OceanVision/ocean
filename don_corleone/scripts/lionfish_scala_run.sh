#!/bin/bash
source ./init.sh
echo "Running Lionfish Scala"
if [[ ! -f ../lionfish/lionfish.jar ]]; then
    echo "Packaging lionfish into lionfish.jar"
    cd ../lionfish && sudo -E sbt one-jar
    cd ../lionfish && sudo -E find target -type f -name "*-one-jar.jar" -exec mv {} lionfish.jar \;
    echo "Packaged lionfish into lionfish.jar"
fi

cd ../lionfish && sudo java -jar lionfish.jar "${@:1}"
