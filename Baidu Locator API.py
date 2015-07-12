# -*- coding: utf-8 -*-

# Locator for Baidu Map
# Supplementary for Geocoder

# Requirement: Python 3.x
# Developer: Xiaoxing Qin@Sun Yat-sen University
# Acknowledgement: Kejing Peng@Microsoft provided instructions
# License: Free for non-commercial use

# Instruction
# 1. Register a personal Baidu API key and replace it in main function
# 2. Specify city in main function
# 3. Specify BD09 to WGS04 conversion in Locate function (see Baidu Place API.py)
# 4. Format address data according to Input/Ungeocoded Address.csv
# 5. Run the script

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
def BD09MCToBD09(apikey, lng, lat):
    coords = str.format("{0},{1}", lng, lat)
    url = str.format("http://api.map.baidu.com/geoconv/v1/?&ak={0}&coords={1}&from=6&to=5", apikey, coords)
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))

    bd09 = []
    if 'result' in data:
        r = data['result']
        bd09 = [r[0]['x'], r[0]['y']]

    return bd09

def Locate(apikey, city_code, address):
    url = str.format("http://api.map.baidu.com/?qt=s&c={0}&wd={1}", city_code, urllib.parse.quote(address))
    DownloadPage(url, "temp.txt")
    f = codecs.open("temp.txt", "r", encoding = "utf-8")
    data = json.loads(f.read())
    f.close()  
        
    lat_bd09mc = lng_bd09mc = lat_bd09 = lng_bd09 = lat_wgs84 = lng_wgs84 = ''
    
    if 'content' in data:
        r = data['content'][0]
        
        if 'ext' in r:            
            lng_bd09mc = r['ext']['detail_info']['point']['x']
            lat_bd09mc = r['ext']['detail_info']['point']['y']

            # BD09MC to BD09
            bd09 = BD09MCToBD09(apikey, lng_bd09mc, lat_bd09mc)
            lng_bd09 = bd09[0]
            lat_bd09 = bd09[1]            
            
            # BD09 to WGS04 conversion (region-dependent)
            lng_wgs84 = -0.081774703936586 + 1.00062621134481 * lng_bd09 - 0.0000472322372012116 * lat_bd09
            lat_wgs84 = -0.0398742657492583 + 0.000368742795507935 * lng_bd09 + 0.999770842271639 * lat_bd09            

    return str.format("{0},{1},{2},{3},{4},{5}", lat_bd09mc, lng_bd09mc, lat_bd09, lng_bd09, lat_wgs84, lng_wgs84)

if __name__ == '__main__':
    # Setting
    apikey = "cnbF6dk3m8fohmVcnniirI6I"
    city = "广州"
    city_code = 257

    # Geocode address
    start = datetime.now()
    print(str.format("Geocoding Address in {0} ({1})", city, start))

    f_in = codecs.open("Input/Ungeocoded Address.csv", "r", encoding = "utf-8-sig").readlines()
    f_out = codecs.open("Output/Located Address.csv", "w", encoding = "utf-8-sig")
    f_out.write("OBJECTID,Address,Latitude_BD09MC,Longitude_BD09MC,Latitude_BD09,Longitude_BD09,Latitude_WGS84,Longitude_WGS84\n")

    f_err = codecs.open("Output/Locating Error.csv", "w", encoding = "utf-8-sig")
    f_err.write("OBJECTID,ADDRESS\n")

    for f in f_in[1:]:
        try:
            r = f.strip().split(',')
            oid = r[0]
            address = r[1]            
            location = Locate(apikey, city_code, address)
            f_out.write(str.format("{0},{1},{2}\n", oid, address, location))
        except:
            f_err.write(f)
            continue
                        
    f_out.close()
    f_err.close()
    os.remove("temp.txt")

    end = datetime.now()
    print(str.format("Completed ({0})", end))
    print(str.format("Duration: {0}", end - start))
