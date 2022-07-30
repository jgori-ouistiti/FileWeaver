#!/bin/bash
find /home/gozea/Documents/Fileweaver/FileWeaver_Partition -maxdepth 1 -mindepth 1 -not -name 'scenario*' | xargs rm -rf
cp -r /home/gozea/Documents/Fileweaver/FileWeaver//scenarios/scenario_hw/files/* /home/gozea/Documents/Fileweaver/FileWeaver_Partition/
chmod u+w /home/gozea/Documents/Fileweaver/FileWeaver_Partition*.tex
chmod u+w /home/gozea/Documents/Fileweaver/FileWeaver_Partition*.py

