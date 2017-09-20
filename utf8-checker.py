

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


def checkEncoding(inList):
    outList = []
    for file in inList:
        body = None
        with open(file, 'r') as f:
            try:
                body = f.read()
            except UnicodeDecodeError:
                outList.append(file)
                pass
        f.closed

    return outList



def main(argv):

    parser = argparse.ArgumentParser(description='UTF-8 file finder')

    parser.add_argument('-f', '--files', dest='fileFilter', metavar='<filter>', nargs='*',
                        help='regex file filter, e.g. -f "\.c$"', default='.')
    parser.add_argument('-r', dest='recursive', action='store_true', default=False,
                            help='Recursive file search')
    parser.add_argument('-p', '--path', dest='path', metavar='<path>', nargs=1,
                        help='root path to files', default='./')
    args = parser.parse_args(argv)

    fileFilter = ''
    for item in args.fileFilter:
        fileFilter = fileFilter + item

    print("Root path '{}'".format(args.path[0]))
    print("file filter regex '{}'".format(fileFilter))

    list1 = applyFileFilter(args.path[0], fileFilter, args.recursive)
    list2 = checkEncoding(list1)

    for item in list2:
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
