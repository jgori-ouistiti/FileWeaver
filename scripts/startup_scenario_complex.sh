#!/bin/bash
rm -f /home/gozea/.cookbook/graph.graphml
rm -f /home/gozea/.cookbook/namemap.pickle
rm -f /home/gozea/Documents/Fileweaver/FileWeaver/.exchange.json
rm -f /home/gozea/Documents/Fileweaver/FileWeaver/exchange.json
gh="https://github.com/AllenDowney/ThinkDSP"
rm -rf /home/gozea/Documents/Fileweaver/FileWeaver_Partition
git clone $gh /home/gozea/Documents/Fileweaver/FileWeaver_Partition
rm -rf /home/gozea/Documents/Fileweaver/FileWeaver_Partition/.git
/home/gozea/Documents/Fileweaver/FileWeaver//scenarios/complex/scnr.sh
