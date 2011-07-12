#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import string
import re
import mimetypes
import base64

from optparse import OptionParser

version = u'0.1'
compPrefix ='_comp'

def dataURL(imgfile):
    mimetype =  mimetypes.guess_type(imgfile)[0]
    allData = open(imgfile).read()
    data = "'data:"+mimetype+";base64,"+base64.b64encode(allData).strip()+"'"
    return data


def run(args, options):
    css_file = options.infile
    mime = mimetypes.guess_type(css_file)[0]
    
    if (os.path.isfile( css_file ) and mime =="text/css"):
        filename, ext = os.path.splitext( os.path.basename(css_file) )
        css_path = os.path.dirname( os.path.abspath( css_file ) )
        css_body = ""
        
        if options.outfile == None:
            out_file = filename + compPrefix + ext
        else :
            out_file = options.outfile
        
        with open(css_file) as f:
            for line in f:
                css_body += line.strip()

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
            if os.path.isfile(img_url) :
                data = dataURL(img_url)
                css_body = re.sub(img_url, data, css_body)
 
        try:
            f = open(out_file, 'w')
            f.writelines(css_body)
        finally:
            f.close()
            print "compCSS: " + css_file + " -> " + out_file


def main():
    usage = 'usage: %prog [options] CSS_file'
    parser = OptionParser(usage=usage)
    parser.add_option('-f', '--filename', action='store', dest='infile',
        help='Input CSS file to read data from')
    parser.add_option('-o', '--output', action='store', dest='outfile',
        help='Output CSS file to write data to')

    origin_dir = os.getcwd()
    (options, args) = parser.parse_args()
    if options.infile :
        run(args, options)
    
    os.chdir(origin_dir)

if __name__ == '__main__':
    main()