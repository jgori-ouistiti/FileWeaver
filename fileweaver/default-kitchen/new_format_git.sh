#!/bin/bash
#### $1 = repo, $2 = Extension, $3 = filename, $4 = cookbookleftpage
cd $1
git branch FORMAT-$2
git checkout FORMAT-$2
cat $3 > $4
git commit -a -m "New Format"
rm $3
