#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import string
import re
import mimetypes
import base64

from optparse import OptionParser

version = "%prog 0.1"
compPrefix ='_comp'

def dataURL(imgfile):
    if os.path.isfile(imgfile) :
        mimetype =  mimetypes.guess_type(imgfile)[0]
        if mimetype.index('image') >= 0 : 
            allData = open(imgfile).read()
            data = "'data:"+mimetype+";base64,"+base64.b64encode(allData).strip()+"'"
            return data
    return False


def compress( css_file ):
    mime = mimetypes.guess_type(css_file)[0]
    if (os.path.isfile( css_file ) and mime =="text/css"):
        css_path = os.path.dirname( os.path.abspath( css_file ) )
        css_body = ""
        
        with open(css_file) as f:
            for line in f:
                l = line.strip()
                importFiles = re.findall(r'(@import (url)?[\(\'\"]*([^\'\"\)]*)[\'\"\)]*;)',l)
                if len(importFiles) > 0 :
                    css_file = css_path + "/"+ importFiles[0][2]
                    l = compress( css_file )
                css_body += l

        css_body = re.sub(r'\r','', css_body)
        css_body = re.sub(r'[\t\n]','', css_body)
        css_body = re.sub(r'[\s]+',' ', css_body)
        css_body = re.sub(r'\/\*.*?\*\/','', css_body)
        css_body = re.sub(r'[\s]*:[\s]*',':', css_body)
        css_body = re.sub(r';[\s]*',';', css_body)
        css_body = re.sub(r'[\s]*{[\s]*','{', css_body)
        css_body = re.sub(r'}','}\n', css_body)

        os.chdir(css_path)
        img_urls = re.findall(r'url\([\'\"]?(.*)[\'\"]?\)',css_body)
        for img_url in img_urls:
            data = dataURL(img_url)
            if data != False :
                css_body = re.sub(img_url, data, css_body)
        
        return css_body

    else :
        return False

def run(args, options):
    css_file = options.infile
    css_body = compress( css_file )
    
    if css_body != False :
        filename, ext = os.path.splitext( os.path.basename(css_file) )
        if options.outfile == None:
            out_file = filename + compPrefix + ext
        else :
            out_file = options.outfile

        try:
            f = open(out_file, 'w')
            f.writelines(css_body)
            print "compCSS: " + css_file + " -> " + out_file
        finally:
            f.close()

def main():
    usage = 'usage: %prog [options] CSS_file'
    parser = OptionParser(usage=usage, version=version )
    parser.add_option('-f', '--filename', action='store', dest='infile',
        help='Input CSS file to read data from')
    parser.add_option('-o', '--output', action='store', dest='outfile',
        help='Output CSS file to write data to')

    origin_dir = os.getcwd()

    (options, args) = parser.parse_args()
    sysArgv = sys.argv
    if options.infile :
        run(args, options)
    else :
        if len(sysArgv) == 2:
            options.infile = sysArgv[1]
            run(args, options)
    
    os.chdir(origin_dir)

if __name__ == '__main__':
    main()