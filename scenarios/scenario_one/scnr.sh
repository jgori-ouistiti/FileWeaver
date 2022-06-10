#!/bin/bash
find /home/alexandre/Documents/StageM1/FileWeaver_Partition -maxdepth 1 -mindepth 1 -not -name 'scenario*' | xargs rm -rf
cp -r /home/alexandre/Documents/StageM1/FileWeaver//scenarios/scenario_one/files/* /home/alexandre/Documents/StageM1/FileWeaver_Partition/
chmod u+w /home/alexandre/Documents/StageM1/FileWeaver_Partition*.tex
chmod u+w /home/alexandre/Documents/StageM1/FileWeaver_Partition*.py
