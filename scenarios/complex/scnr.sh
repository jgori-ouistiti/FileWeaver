#!/bin/bash
rsync -av --progress /home/alexandre/Documents/StageM1/FileWeaver//scenarios/complex/files /home/alexandre/Documents/StageM1/FileWeaver_Partition --exclude src

 mkdir /home/alexandre/Documents/StageM1/FileWeaver_Partition/../src
cp /home/alexandre/Documents/StageM1/FileWeaver//scenarios/complex/files/src/* /home/alexandre/Documents/StageM1/FileWeaver_Partition/../src