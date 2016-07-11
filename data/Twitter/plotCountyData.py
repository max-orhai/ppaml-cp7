"""
Plot values associated with US counties on a US map

Some code is from:
http://flowingdata.com/2009/11/12/how-to-make-a-us-county-thematic-map-using-free-tools/

@author: Ssu-Hsin Yu (syu001@gmail.com)
"""

from bs4 import BeautifulSoup

## Plot county map in color proportional to given values of the counties
#
# @param CntyData: dictionary storing county data whose keys are county
#   FIPS code and values are the data to be plotted.
#   {'01001': 15.2; ...}   
# @param map_file: US county map in the SVG format
# @param outmap_fn: file to store the resultant SVG plot (default test.svg)
# @param colors: (optional) list of hexadecimal (HEX) colors. For example,
#   ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]
# @param min_val: min value to scale the colors. If None, min_val is equal to
#   the minimum value of the data
# @param max_val: max value to scale the colors. If None, max_val is equal to
#   the maximum value of the data
def plotCountyData(CntyData, map_file, outmap_fn='test.svg', colors=None, min_val=None, max_val=None):

    # Load the SVG map
    with open(map_file, 'r') as fobj:
        svg = fobj.read()
    
    # Load into Beautiful Soup
    soup = BeautifulSoup(svg, selfClosingTags=['defs','sodipodi:namedview'])

    # Find counties in SVG
    paths = soup.findAll('path')

    # colormap
    if colors is None: # default colormap
        # Map colors
        colors = ['#fff7ec','#fee8c8','#fdd49e','#fdbb84','#fc8d59','#ef6548',
                  '#d7301f','#b30000','#7f0000']
        #colors = ['#f7f4f9','#e7e1ef','#d4b9da','#c994c7','#df65b0','#e7298a',
        #          '#ce1256','#980043','#67001f']
        #colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]

    # County style
    path_style = 'font-size:12px;fill-rule:nonzero;stroke:#FFFFFF;stroke-opacity:1;stroke-width:0.1;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;marker-start:none;stroke-linejoin:bevel;fill:'
    
    # minimal value
    if min_val is None:
        min_val = min(CntyData.values())
    # maximal value
    if max_val is None:
        max_val = max(CntyData.values())

    # Color the counties based on their corresponding values by changing the SVG map
    for p in paths:
        
        if p['id'] not in ["State_Lines", "separator"]:
            try:
                data = CntyData[p['id']]
            except:
                continue

            # quantize the data into colors
            color_class = int(float(len(colors)-1)*float(min(data,max_val)-min_val) /
                              float(max_val-min_val))
            color = colors[color_class]

            # append the color to the end of style string (right after 'fill:')
            p['style'] = path_style + color


    # Output map
    with open(outmap_fn,'wb') as fobj:
        fobj.write(soup.prettify())
