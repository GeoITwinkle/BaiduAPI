# -*- coding: utf-8 -*-

# Geocoder for Baidu Map

# Requirement: Python 3.x
# Developer: Xiaoxing Qin@Sun Yat-sen University
# Acknowledgement: Kejing Peng@Microsoft solved UTF-8 issues
# License: Academic use only

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

def Geocode(access, city, address):
    url = str.format("{0}&output=json&city={1}&address={2}", access, urllib.parse.quote(city), urllib.parse.quote(address))
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
            gcj02 = MapProjection.BD09ToGCJ02(lat_bd09, lng_bd09)
            wgs84 = MapProjection.GCJ02ToWGS84_Exact(gcj02['lat'], gcj02['lon'])
            lat_wgs84 = wgs84['lat']
            lng_wgs84 = wgs84['lon']
            
        if 'precise' in r:
            precise = r['precise']
            
        if 'confidence' in r:
            confidence = r['confidence']
            
        if 'level' in r:
            level = r['level']

    return str.format("{0},{1},{2},{3},{4},{5},{6}", lat_bd09, lng_bd09, lat_wgs84, lng_wgs84, precise, confidence, level)

def Process(apikey, city):
    start = datetime.now()
    print(str.format("Geocoding address in {0} ({1})", city, start))

    f_in = codecs.open("Input/Address.csv", "r", encoding = "utf-8-sig")
    f_out = codecs.open("Output/Geocoded Address.csv", "w", encoding = "utf-8-sig")
    f_out.write("OBJECTID,Address,Latitude_BD09,Longitude_BD09,Latitude_WGS84,Longitude_WGS84,Precise,Confidence,Level\n")

    f_err = codecs.open("Output/Geocoding Error.csv", "w", encoding = "utf-8-sig")
    f_err.write("OBJECTID,ADDRESS\n")

    err = 0
    for f in f_in.readlines()[1:]:
        try:
            [oid, address] = f.strip().split(',')            
            geocode = Geocode(access, city, address)
            f_out.write(str.format("{0},{1},{2}\n", oid, address, geocode))
        except:
            f_err.write(f)
            err += 1
            continue

    f_in.close()            
    f_out.close()
    f_err.close()
    os.remove("temp.txt")

    if err == 0:
        os.remove("Output/Geocoding Error.csv")

    end = datetime.now()
    print(str.format("Completed ({0})", end))
    print(str.format("Duration: {0}", end - start))    

if __name__ == '__main__':
    # Configuration
    print("========== Configuration ==========")
    
    f_key = codecs.open("Config/API Key.csv", "r", encoding = "utf-8-sig")
    apikey = f_key.readlines()[1].strip().split(',')[1]
    f_key.close()
    
    access = "http://api.map.baidu.com/geocoder/v2/?ak=" + apikey

    cities = {}
    f_city = codecs.open("Config/City.csv", "r", encoding = "utf-8-sig")
    for f in f_city.readlines()[1:]:
        r = f.strip().split(',')
        cities[r[1]] = r[2]
    
    city = input("City: ")
    if city not in cities:
        print("Invalid city.")
        sys.exit(1)    

    # Geocode address
    print("========== Process ==========")
    Process(apikey, city)
