#!/bin/bash
rm -f /home/alexandre/.cookbook/graph.graphml
rm -f /home/alexandre/.cookbook/namemap.pickle
rm -f /home/alexandre/Documents/StageM1/FileWeaver/.exchange.json
rm -f /home/alexandre/Documents/StageM1/FileWeaver/exchange.json
gh="https://github.com/AllenDowney/ThinkDSP"
rm -rf /home/alexandre/Documents/StageM1/FileWeaver_Partition
git clone $gh /home/alexandre/Documents/StageM1/FileWeaver_Partition
rm -rf /home/alexandre/Documents/StageM1/FileWeaver_Partition/.git
/home/alexandre/Documents/StageM1/FileWeaver//scenarios/complex/scnr.sh
