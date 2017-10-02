

import argparse
import os
import re
import shutil
import sys


def applyFileFilter(path, filter, recursive):
    # Figure out how the path gets dealt with and/or included in the regex and thus the
    # actual root of the tree walk

    fileList = []

    if recursive:
        for root, subDir, files in os.walk(path, topdown=True, followlinks=False):
            for file in files:
                if re.search(filter, file):
                # if filter in file:
                    # if filter.match(fname):
                    fullFilePath = os.path.join(root, file)
                    fileList.append(fullFilePath)
    else:
        ls = os.listdir(path)
        for file in ls:
            if re.search(filter, file):
            # if filter in file:
                fullFilePath = os.path.join(path, file)
                fileList.append(fullFilePath)

    # for file in fileList:
    #    print(file)

    return fileList

def requiresInclude(inList, header):
    outList = []

    includeRegexPrefix = '\s*#\s*include\s+"'
    includeRegex = includeRegexPrefix + header

    outList = []
    for file in inList:
        if header in file:
            continue
        with open(file, 'r') as f:
            try:
                body = f.read()
            except:
                print(file)
                raise
        f.closed

        if not re.search(includeRegex, body):
            outList.append(file)

    return outList

def applyGrepFilter(inList, regex):
    outList = []
    for file in inList:
        body = None
        with open(file, 'r') as f:
            try:
                body = f.read()
            except:
                print(file)
                raise
        f.closed

        if re.search(regex, body):
            outList.append(file)

    return outList

def appendInclude(file, includeToAppend):
     includeRegex = '\s*#\s*include\s+"'
     include = '#include "{}"\n'.format(includeToAppend)

     contents = []
     with open(file, 'r') as f:
         try:
             contents = f.readlines()
         except:
             print(file)
             raise
     f.closed

     lineNumber = 0
     needsWrite = False
     for line in contents:
         if re.search(includeRegex, line):
             contents.insert(lineNumber, include)
             needsWrite = True
             break
         lineNumber += 1

    # account for no existing includes section
    # but where to add them? What about .h and guards, e.g. can't just add at
    # beg of file. run again in --listOnly to make user aware

     if needsWrite:
         with open(file, 'w') as f:
             contents = "".join(contents)
             f.write(contents)
         f.closed

def main(argv):

    parser = argparse.ArgumentParser(description='C/C++ include organizer')
    parser.add_argument(dest='include', metavar='<include>',
                        help='header to include, e.g. my_header.h')
    parser.add_argument('-f', '--files', dest='fileFilter', metavar='<filter>', nargs=1,
                        help='regex file filter, e.g. -f "\.c$"', default='.')
    parser.add_argument('-r', dest='recursive', action='store_true', default=False,
                            help='Recursive file search')
    parser.add_argument('-p', '--path', dest='path', metavar='<path>', nargs=1,
                        help='root path to files', default='./')
    parser.add_argument('--regex', dest='regex', metavar='<expression>', nargs='*',
                        help='regex to grep files', default='.')
    parser.add_argument('--listOnly', dest='listOnly', action='store_true', default=False,
                            help='Only list files that need fixing - does not do actual fix')
    args = parser.parse_args(argv)

    fileFilter = args.fileFilter[0]  # re.compile(args.fileFilter[0])
    # compiledGrepFilter = args.regex[0]#re.compile(args.regex[0])
    regex = ''
    for item in args.regex:
        regex = regex + item

    print("Root path '{}'".format(args.path[0]))
    print("regex '{}'".format(regex))
    print("File to include '{}'".format(args.include))
    print("file filter regex '{}'".format(fileFilter))

    list1 = applyFileFilter(args.path[0], fileFilter, args.recursive)
    list2 = applyGrepFilter(list1, regex)
    list3 = requiresInclude(list2, args.include)

    for item in list3:
        if args.listOnly:
            print(item)
        else:
            appendInclude(item, args.include)

    if not args.listOnly:
        list4 = requiresInclude(list2, args.include)
        if list4:
            print('ERROR: The following files need manual editing!')
            for item in list4:
                print(item)


    # for item in list2:
    #    print(item)

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except OSError as err:
        sys.exit('ERROR: {0}'.format(err))
    except:
        # add proper error handling and logging etc
        raise
