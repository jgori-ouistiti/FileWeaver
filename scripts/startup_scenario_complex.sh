#!/bin/bash
rm -f /home/alexandre/.cookbook/graph.graphml
rm -f /home/alexandre/.cookbook/namemap.pickle
rm -f /home/alexandre/Documents/StageM1/FileWeaver/.exchange.json
rm -f /home/alexandre/Documents/StageM1/FileWeaver/exchange.json
gh="https://github.com/AllenDowney/ThinkDSP"
git clone $gh /home/alexandre/Documents/StageM1/FileWeaver_Partition