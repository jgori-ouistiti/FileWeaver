#!/bin/bash
rm -f /home/gozea/.cookbook/graph.graphml
rm -f /home/gozea/.cookbook/namemap.pickle
rm -f /home/gozea/Documents/Fileweaver/FileWeaver/.exchange.json
rm -f /home/gozea/Documents/Fileweaver/FileWeaver/exchange.json
gh="https://github.com/AllenDowney/ThinkDSP"
git clone $gh /home/gozea/Documents/Fileweaver/FileWeaver_Partition