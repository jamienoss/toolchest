import argparse
import os
import sys
import re

from astropy.io import fits

def applyFileFilter(path, filter):
    # Figure out how the path gets dealt with and/or included in the regex and thus the
    #actual root of the tree walk

    fileList = []

    for root, subDir, files in os.walk(path, topdown=True, followlinks=False):
        for fname in files:
            if filter in fname:
                #if filter.match(fname):
                fullFilePath = os.path.join(root, fname)
                fileList.append(fullFilePath)

    return fileList

def applyKeywordFilter(inputList, filter):
    # This actually needs to handle filter expressions
    
    filteredList = inputList#list(inputList)

    #Assumes all ops between keyword-value pairs are ANDs
    for item in filter:
        parsedFilter = re.split('=', item)
        keyword = parsedFilter[0]
        value = parsedFilter[1]

        for file in filteredList:
            try:
                hdu = fits.open(file, ignore_missing_end=True)
            except OSError as err:
                pass  # do nothing
            try:
                valueFound = hdu[0].header[keyword]
            except KeyError:
                hdu.close()
                continue
    
            if valueFound == None:
                hdu.close()
                continue
            hdu.close()
    
            if type(valueFound) is bool:
                if valueFound != value:
                    filteredList.remove(file)
            elif value != str.lower(valueFound):
                filteredList.remove(file)
                
    return filteredList

def main(argv):
    parser = argparse.ArgumentParser(description='fits file header filter')
    parser.add_argument('-k', '--keywords', dest='keywordFilter', metavar='<filter>', nargs='+',
                        help='keyword(s) filter(s), e.g. -k data=2017 & instrument=wfc3', default=None)
    parser.add_argument('-f', '--files', dest='fileFilter', metavar='<filter>', nargs=1,
                        help='regex file filter, e.g. -f *raw.fits', default='*')
    parser.add_argument('--silent', dest='silent', action='store_true', default=False,
                            help='Only output final list and nothing else')
    parser.add_argument('--nolist', dest='nolist', action='store_true', default=False,
                            help='Only output stats and not final list')
    args = parser.parse_args(argv)
    
    compiledFileFilter = args.fileFilter[0]#re.compile(args.fileFilter[0])
    
    list = applyFileFilter('./', compiledFileFilter)
    if not args.silent:
        print('{0} files found matching file filter regex'.format(len(list)))
    #for item in list:
    #    print(item)
    
    if not len(list):
        return 0

    finalList = applyKeywordFilter(list, args.keywordFilter)

    if not args.nolist:
        for item in finalList:
            print(item)
    
    if not args.silent:
        print('{0} files found matching file filter AND keyword filter '.format(len(finalList)))
    
if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except OSError as err:
        sys.exit('ERROR: {0}'.format(err))
    except:
        # add proper error handling and logging etc
        raise