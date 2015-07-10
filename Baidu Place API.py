# -*- coding: utf-8 -*-

# POI Data Decoder for Baidu Map

# Requirement: Python 3.x
# Developer: Xiaoxing Qin@Sun Yat-sen University
# Acknowledgement: Kejing Peng@Microsoft solved UTF-8 issues
# License: Free for non-commercial use

# Instruction
# 1. Register a personal Baidu API key and replace it in main function
# 2. Specify POI in main function
# 3. Specify region and extent (lower-left and upper-right in WGS84) in main function
# 4. Specify the limit in main function
#   (1) 20: smaller area, more data, slower speed
#   (2) 760: larger area, less data, faster speed
#   (3) Caution: number of records retrieved from Baidu Map is dynamic and scalable
# 5. Specify BD09 to WGS04 conversion in GetData function
#   (1) In ArcGIS, create a FishNet for the region with high resolution (e.g., 100m for Guangzhou)
#   (2) Get the WGS84 coordinates of cell centroids
#   (3) Convert coordinates from WGS84 to BD09 via Baidu Coordinate API.py
#   (4) Open the output file in Excel, run linear regression to get B0, B1, and B2 in high precision:
#       X_WGS84 = B0 + B1 * X_BD09 + B2 * Y_BD09
#       Y_WGS84 = B0 + B1 * X_BD09 + B2 * Y_BD09
# 6. Run the script

import urllib.request, json, codecs, os
from datetime import datetime

# Utils function
def DownloadPage(url, path):
    try:
        print(url)
        conn = urllib.request.urlopen(url)
        fw = open(path, 'wb')
        fw.write(conn.read())
        fw.close()
    except:
        print("Page not found")
        return

# Convert WGS84 to BD09
def WGS84ToBD09(apikey, extent):
    coords = str.format("{0},{1};{2},{3}", extent[0], extent[1], extent[2], extent[3])
    url = str.format("http://api.map.baidu.com/geoconv/v1/?&ak={0}&coords={1}&from=1&to=5", apikey, coords)
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))

    bd09 = []
    if 'result' in data:
        r = data['result']
        bd09 = [r[0]['x'], r[0]['y'], r[1]['x'], r[1]['y']]

    return bd09

# Get POI data
def GetData(url):
    DownloadPage(url, "temp.txt")
    f = codecs.open("temp.txt", "r", encoding = "utf-8")  
    data = json.loads(f.read())
    f.close()

    rs = ''

    if 'results' in data:    
        results = data['results']
        for r in results:
            name = lat_bd09 = lng_bd09 = lat_wgs84 = lng_wgs84 = address = telephone = tag = uid = ''

            if 'name' in r:
                name = r['name']
                
            if 'location' in r:                
                lat_bd09 = r['location']['lat']            
                lng_bd09 = r['location']['lng']
                # BD09 to WGS04 conversion (region-dependent)
            lat_wgs84 = -0.0398742657492583 + 0.000368742795507935 * lng_bd09 + 0.999770842271639 * lat_bd09
            lng_wgs84 = -0.081774703936586 + 1.00062621134481 * lng_bd09 - 0.0000472322372012116 * lat_bd09
                
            if 'address'in r:
                address = r['address']
                
            if 'telephone' in r:
                telephone = r['telephone']
                
            if 'uid' in r:
                uid = r['uid']
                
            if 'detail_info' in r:
                tag = r['detail_info']['tag']

            rs = rs + str.format("{0},\"{1}\",{2},{3},{4},{5},\"{6}\",\"{7}\",\"{8}\"\n", uid, name, lat_bd09, lng_bd09, lat_wgs84, lng_wgs84, address, telephone, tag)

    return rs

# Search for POI by extent
def SearchByExtent(access, poi, extent, limit):
    [x1, y1, x2, y2] = extent
    url = str.format("{0}&query={1}&bounds={2},{3},{4},{5}&output=json&page_size=20", access, urllib.parse.quote(poi), y1, x1, y2, x2)

    # Get the number of records in extent    
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))   
    total = -1
    if 'total' in data:
        total = data['total']

    # Quadrant search
    r = ''
    if total <= 0:
        r = '' 
    elif total <= limit:
        for i in range(0, int((total - 1) / 20) + 1):
            curr_url = str.format("{0}&page_num={1}", url, i)
            r = r + GetData(curr_url)
    else:        
        ext_ne = [(x1 + x2) / 2, (y1 + y2) / 2, x2, y2]
        ext_nw = [x1, (y1 + y2) / 2, (x1 + x2) / 2, y2]
        ext_sw = [x1, y1, (x1 + x2) / 2, (y1 + y2) / 2]
        ext_se = [(x1 + x2) / 2, y1, x2, (y1 + y2) / 2]
        r = SearchByExtent(access, poi, ext_ne, limit) + SearchByExtent(access, poi, ext_nw, limit) + SearchByExtent(access, poi, ext_sw, limit) + SearchByExtent(access, poi, ext_se, limit)

    return r

if __name__ == '__main__':
    # Setting
    apikey = "cnbF6dk3m8fohmVcnniirI6I"
    access = "http://api.map.baidu.com/place/v2/search?ak=" + apikey
    region = "广州"
    extent = [112.956429, 22.557131, 114.055893, 23.936867]
    poi = ["地铁", "大学"]
    limit = 760

    # Get POI data
    for  p in poi:
        start = datetime.now()
        print(str.format("POI data of {0} in {1}:", p, region))
        print(str.format("Retrieving ({0})", start))
        
        # Convert extent from WGS84 to BD09
        ext_bd09 = WGS84ToBD09(apikey, extent)            
        
        # Retrieve data
        fname = str.format("Output/{0}_{1}.csv", region, p)
        f = codecs.open(fname, "w",  encoding = "utf-8-sig")
        f.write("UID,Name,Latitude_BD09,Longitude_BD09,Latitude_WGS84,Longitude_WGS84,Address,Telephone,Tag\n")        
        f.write(SearchByExtent(access, p, ext_bd09, limit))
        f.close()
        os.remove("temp.txt")

        end = datetime.now()
        print(str.format("Completed ({0})", end))
        print(str.format("Duration: {0}", end - start))
