#!/usr/bin/env bash
if [ $2 = '1' ];
then
	strace -ff --trace=file $1 2>&1 | grep O_CREAT | awk -F '"' '{print $2}'
elif [ $2 = '2' ];
then
	strace -ff --trace=file $1 2>&1 | grep O_RDONLY | awk -F '"' '{print $2}'
else
	strace -ff --trace=file $1 2>&1 | grep 'O_RDONLY\|O_CREAT' | awk -F '"' '{print $2}'
fi
