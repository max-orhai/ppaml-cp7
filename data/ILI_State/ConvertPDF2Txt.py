"""
Convert PDF files to text files

@author: syu
"""

#import PyPDF2, slate
import os
from subprocess import call

## Get all the PDF files and convert them to text files
pdfFiles = []
path = '2011-2012'
for filename in os.listdir(path):
    if filename.endswith('.pdf'):
        pdfFiles.append(filename)
        pdfName = os.path.join(path, filename)
        txtName = filename.split(os.extsep)[0] + '.txt'
        call(['pdf2txt.py', '-o'+txtName, pdfName])


### Don't work
#for filename in pdfFiles:
#    with open(os.path.join(path,filename), 'rb') as pdfFileObj:
#        pageObj = slate.PDF(pdfFileObj)
#        pdfText = pageObj[0]
#        pdfFileObj.close()
#        
#        
#        #pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
#        #pageObj = pdfReader.getPage(0)
#        #pdfText = pageObj.extractText()
#
#with open(os.path.join(path,filename), 'rb') as pdfFileObj:
#    pageObj = slate.PDF(pdfFileObj)
#    pdfFileObj.close()
#
#
#with open(os.path.join(path,filename), 'rb') as pdfFileObj:
#    pageObj = slate.PDF(pdfFileObj)
#    pdfText = pageObj[0]
#    pdfFileObj.close()
