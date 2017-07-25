import argparse
import os
import sys
import re
import shutil

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
    
    filteredList = []

    #Assumes all ops between keyword-value pairs are ANDs
    for file in inputList:
        #try:
        hdu = fits.open(file, ignore_missing_end=True)
        #except OSError as err:
        #    filteredList.remove(file)
        #    continue  # do nothing
        
        for item in filter:
            parsedFilter = re.split('=', item)
            keyword = parsedFilter[0]#.lower()
            value = parsedFilter[1]#.lower()
            #print('Filtering list by "{0}"="{1}"...'.format(keyword, value))
        
            try:
                valueFound = hdu[0].header[keyword]
            except KeyError:
                hdu.close()
                continue
    
            if valueFound == None:
                hdu.close()
                continue
            hdu.close()
   
            #print('value found "{0}"'.format(valueFound))
            if type(valueFound) is bool:
                if valueFound == value:
                    filteredList.append(file)
            elif value.lower() == str.lower(valueFound):
                filteredList.append(file)
                
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
    parser.add_argument('-c', dest='copyToPath', metavar='<path>', nargs=1, type=str,
                             help='Copy all matching data to <path>', default=None)
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
    
    if args.copyToPath:
        for item in finalList:
            print('Copying "{0}"...'.format(item))
            shutil.copy(item, args.copyToPath[0])
 
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