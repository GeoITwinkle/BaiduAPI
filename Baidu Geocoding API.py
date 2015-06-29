# -*- coding: utf-8 -*-

# Geocoder for Baidu Map

# Requirement: Python 3.x
# Developer: Xiaoxing Qin@Sun Yat-sen University
# Acknowledgement: Kejing Peng@Microsoft solved UTF-8 issues
# License: Free for non-commercial use

# Instruction
# 1. Register a personal Baidu API key and replace it in main function
# 2. Specify city in main function
# 3. Specify BD09 to WGS04 conversion in Geocoding function (see Baidu Place API.py)
# 4. Format address data according to Input/Address.csv
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

def Geocoding(access, city, address):
    url = str.format("{0}&city={1}&address={2}&output=json", access, urllib.parse.quote(city), urllib.parse.quote(address))
    DownloadPage(url, "temp.txt")
    f = codecs.open("temp.txt", "r", encoding = "utf-8")
    data = json.loads(f.read())
    f.close()

    lat_bd09 = lng_bd09 = lat_wgs84 = lng_wgs84 = precise = confidence = level = ''

    if 'result' in data:
        r = data['result']
        
        if 'location' in r:                
            lat_bd09 = r['location']['lat']            
            lng_bd09 = r['location']['lng']
            # BD09 to WGS04 conversion
            lat_wgs84 = -0.039884925 + 0.000368817 * lng_bd09 + 0.999770936 * lat_bd09
            lng_wgs84 = -0.081791896 + 1.00062635 * lng_bd09 - 0.0000471711 * lat_bd09
            
        if 'precise' in r:
            precise = r['precise']
            
        if 'confidence' in r:
            confidence = r['confidence']
            
        if 'level' in r:
            level = r['level']

    return str.format("{0},{1},{2},{3},{4},{5},{6}", lat_bd09, lng_bd09, lat_wgs84, lng_wgs84, precise, confidence, level)

if __name__ == '__main__':
    # Setting
    apikey = "cnbF6dk3m8fohmVcnniirI6I"
    access = "http://api.map.baidu.com/geocoder/v2/?ak=" + apikey
    city = "广州"

    # Geocode address
    start = datetime.now()
    print(str.format("Geocoding Address in {0} ({1})", city, start))

    f_in = open("Input/Address.csv", "r").readlines()
    f_out = codecs.open("Output/Geocoded Address.csv", "w",  encoding = "utf-8-sig")
    f_out.write("OBJECTID,Address,Latitude_BD09,Longitude_BD09,Latitude_WGS84,Longitude_WGS84,Precise,Confidence,Level\n") 

    for f in f_in[1:]: 
        r = f.replace('\n', '').split(',')
        oid = r[0]
        address = r[1]
        f_out.write(str.format("{0},{1},{2}\n", oid, address, Geocoding(access, city, address)))

    f_out.close()
    os.remove("temp.txt")

    end = datetime.now()
    print(str.format("Completed ({0})", end))
    print(str.format("Duration: {0}", end - start))
