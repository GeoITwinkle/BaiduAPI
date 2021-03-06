# -*- coding: utf-8 -*-

# Baidu Place Collector

# Service Provider: Baidu, Inc.
# Developer: Xiaoxing Qin@Sun Yat-sen University
# Acknowledgement: Kejing Peng@Microsoft provided instructions
# License: Academic use only
# Requirement: Python 3.x

import urllib.request, json, codecs, os, sys, MapProjection
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
    url = str.format("http://api.map.baidu.com/geoconv/v1/?&ak={0}&from=1&to=5&coords={1}", apikey, coords)
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))

    if 'result' in data:
        r = data['result']
        return [r[0]['x'], r[0]['y'], r[1]['x'], r[1]['y']]
    else:        
        return None

# Load POI data
def LoadPOI(url):
    DownloadPage(url, "temp.txt")
    f = codecs.open("temp.txt", "r", encoding = "utf-8")  
    data = json.loads(f.read())
    f.close()

    rs = ''

    if 'results' in data:
        for r in data['results']:
            name = lat_bd09 = lon_bd09 = lat_wgs84 = lon_wgs84 = address = telephone = tag = uid = ''

            if 'name' in r:
                name = r['name']
                
            if 'location' in r:                
                lat_bd09 = r['location']['lat']            
                lon_bd09 = r['location']['lng']
                
                # BD09 to WGS04 conversion
                gcj02 = MapProjection.BD09ToGCJ02(lat_bd09, lon_bd09)
                wgs84 = MapProjection.GCJ02ToWGS84_Exact(gcj02['lat'], gcj02['lon'])
                lat_wgs84 = wgs84['lat']
                lon_wgs84 = wgs84['lon']
            
            if 'address'in r:
                address = r['address']
                
            if 'telephone' in r:
                telephone = r['telephone']
                
            if 'uid' in r:
                uid = r['uid']
                
            if 'detail_info' in r:
                tag = r['detail_info']['tag']

            rs = rs + str.format("{0},\"{1}\",{2},{3},{4},{5},\"{6}\",\"{7}\",\"{8}\"\n", uid, name, lat_bd09, lon_bd09, lat_wgs84, lon_wgs84, address, telephone, tag)

    return rs

# Search for POI by extent
def SearchPOI(apikey, poi, extent, limit):
    [x1, y1, x2, y2] = extent
    url = str.format("http://api.map.baidu.com/place/v2/search?ak={0}&output=json&query={1}&bounds={2},{3},{4},{5}&page_size=20", apikey, urllib.parse.quote(poi), y1, x1, y2, x2)

    # Get the number of records in extent    
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))   
    total = data['total'] if 'total' in data else -1

    # Quadrant search
    r = ''
    if total <= 0:
        r = '' 
    elif total <= limit:
        for i in range(0, int((total - 1) / 20) + 1):
            curr_url = str.format("{0}&page_num={1}", url, i)
            r = r + LoadPOI(curr_url)
    else:        
        ext_ne = [(x1 + x2) / 2, (y1 + y2) / 2, x2, y2]
        ext_nw = [x1, (y1 + y2) / 2, (x1 + x2) / 2, y2]
        ext_sw = [x1, y1, (x1 + x2) / 2, (y1 + y2) / 2]
        ext_se = [(x1 + x2) / 2, y1, x2, (y1 + y2) / 2]
        r = SearchPOI(apikey, poi, ext_ne, limit) + SearchPOI(apikey, poi, ext_nw, limit) + SearchPOI(apikey, poi, ext_sw, limit) + SearchPOI(apikey, poi, ext_se, limit)

    return r

# Retrieve POI data
def Process(apikey, poi, city, extent, limit):
    for  p in poi:
        start = datetime.now()
        print(str.format("Retrieving POI data of {0} in {1} ({2})", p, city, start))
        
        # Convert extent from WGS84 to BD09
        ext_bd09 = WGS84ToBD09(apikey, extent)            
        
        # Retrieve data
        path = str.format("Output/{0}_{1}.csv", city, p)
        f = codecs.open(path, "w",  encoding = "utf-8-sig")
        f.write("UID,Name,Latitude_BD09,Longitude_BD09,Latitude_WGS84,Longitude_WGS84,Address,Telephone,Tag\n")

        try:
            result = SearchPOI(apikey, p, ext_bd09, limit)
            f.write(result)
        except Exception as e:
            print("Error: " + str(e))

        f.close()

        if os.path.exists("temp.txt"):
            os.remove("temp.txt")

        end = datetime.now()
        print(str.format("Completed ({0})", end))
        print(str.format("Duration: {0}", end - start))
    
if __name__ == '__main__':
    # Configuration
    print("========== Configuration ==========")
    
    # API key
    f_key = codecs.open("Config/API Key.csv", "r", encoding = "utf-8-sig")
    apikey = f_key.readlines()[1].strip().split(',')[1]
    f_key.close()

    url = str.format("http://api.map.baidu.com/geoconv/v1/?&ak={0}&from=1&to=5&coords=113,23", apikey)
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
    if data['status'] != 0:
        print("Invalid API key.")
        sys.exit(1)

    # City and extent
    cities = {}
    f_city = codecs.open("Config/City.csv", "r", encoding = "utf-8-sig")
    for f in f_city.readlines()[1:]:
        r = f.strip().split(',')
        if all(r[3:]):
            cities[r[1]] = list(map(lambda x: float(x), r[3:]))
        else:
            cities[r[1]] = None
        
    city = input("City: ")
    if city not in cities:
        print("Error: Invalid city.")
        sys.exit(1)
    elif not cities[city]:
        print("Error: Invalid city extent.")
        sys.exit(1)
    else:
        extent = cities[city]

    # POI   
    poi = input("POI (separated by space): ")
    poi = poi.strip().split()
    if not poi:
        print("Error: Invalid POI.")
        sys.exit(1)

    # Search limit
    limit = input("Number of POI per each iterative search (between 20 and 760): ")
    limit = int(limit)
    if not (20 <= limit <= 760):
        print("Error: Invalid number.")
        sys.exit(1)

    # Get POI data
    print("========== Process ==========")
    Process(apikey, poi, city, extent, limit)
