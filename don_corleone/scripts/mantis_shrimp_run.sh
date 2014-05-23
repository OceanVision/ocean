#!/bin/bash
source ./init.sh
echo "Running Mantis Shrimp"
if [[ ! -f ../mantis_shrimp/mantis_shrimp.jar ]]; then
    echo "Packaging Mantis Shrimp into mantis_shrimp.jar"
    cd ../mantis_shrimp && sudo -E sbt one-jar
    cd ../mantis_shrimp && sudo -E find target -type f -name "*-one-jar.jar" -exec mv {} mantis_shrimp.jar \;
    echo "Packaged Mantis Shrimp  into mantis_shrimp.jar"
fi

cd ../mantis_shrimp && sudo java -jar mantis_shrimp.jar "${@:1}"
