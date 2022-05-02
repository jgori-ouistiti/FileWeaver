#!/bin/bash
find /home/juliengori/Documents/FileWeaver_Partition -maxdepth 1 -mindepth 1 -not -name 'scenario*' | xargs rm -rf
cp -r /home/juliengori/Documents/VC/FileWeaver//scenarios/scenario_one/files/* /home/juliengori/Documents/FileWeaver_Partition/
chmod u+w /home/juliengori/Documents/FileWeaver_Partition*.tex
chmod u+w /home/juliengori/Documents/FileWeaver_Partition*.py
