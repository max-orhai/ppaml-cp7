# -*- coding: utf-8 -*-
"""
Download Tennessee weekly ILI reports
"""

import urllib

# url
url = "http://tn.gov/assets/entities/health/attachments/weekxxILI_spnreport_2009.pdf"
filename = "weekxxILI_spnreport_2014.pdf"
#filename = "ILI_spnreport_2013_xx_klm-use.xlsx"

for week in range(1,54):
    url_cur = url.replace("xx",str(week).zfill(2))
    filename_cur = filename.replace("xx",str(week).zfill(2))
    urllib.urlretrieve(url_cur, filename_cur)

