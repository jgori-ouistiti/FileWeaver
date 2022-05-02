#! /usr/bin/python

import sys

print('ready')
while True:
    line = sys.stdin.readline()
    if line == '':
        print('bye')
        sys.exit()

    with open('logfile.txt','a') as fd:
        fd.write(line)

    line = line.rstrip('\n').split(',')

    #### Single file operations
    if 'addFileAndChildren' in line[0]:
        print('OK addFileAndChildren')
        file = line[1]
        # cooking.add_file_and_children(file)
    elif 'copyFileWithDependencies' in line[0]:
        print('OK copyFileWithDependencies')
        file = line[1]
        # managing.copy_link(file)
    else:
        print('ERR unknown command '+line[0])
