#!/bin/bash
rsync -av --progress /home/gozea/Documents/Fileweaver/FileWeaver//scenarios/complex/files /home/gozea/Documents/Fileweaver/FileWeaver_Partition --exclude src

 mkdir /home/gozea/Documents/Fileweaver/FileWeaver_Partition/../src
cp /home/gozea/Documents/Fileweaver/FileWeaver//scenarios/complex/files/src/* /home/gozea/Documents/Fileweaver/FileWeaver_Partition/../src