# -*- coding: utf-8 -*-

# Coordinate Converter for Baidu Map

# Requirement: Python 3.x
# Developer: Xiaoxing Qin@Sun Yat-sen University
# Acknowledgement: Kejing Peng@Microsoft solved UTF-8 issues
# License: Academic use only

# Instruction
# 1. Register a personal Baidu API key and replace it in main function
# 2. Format coordinates data according to Input/WGS84.csv
# 3. Run the script

import urllib.request, json, codecs
from datetime import datetime

def WGS84ToBD09(apikey, wgs84):    
    url = str.format("http://api.map.baidu.com/geoconv/v1/?&ak={0}&coords={1}&from=1&to=5", apikey, wgs84)
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))    
    bd09 = []
    
    if 'result' in data:
        for r in data['result']:
             bd09.append(str.format("{0},{1}", r['x'], r['y']))
             
    return bd09
    
if __name__ == '__main__':
    # Setting
    apikey = "cnbF6dk3m8fohmVcnniirI6I"

    # Convert coordinates
    start = datetime.now()
    print(str.format("Converting WGS84 to BD09. ({0})", start))
    
    f_wgs = codecs.open("Input/WGS84.csv", "r", encoding = "utf-8-sig").readlines()
    f_bd = codecs.open("Output/BD09.csv", "w", encoding = "utf-8-sig")    
    f_bd.write("OBJECTID,X_WGS84,Y_WGS84,X_BD09,Y_BD09\n")

    i = oid = 0
    wgs84 = []
    for f in f_wgs[1:]:
        i += 1
        r = f.strip().split(',')
        wgs84.append(','.join(r[1:]))
        
        if i % 100 == 0 or i == len(f_wgs) - 1:           
            bd09 = WGS84ToBD09(apikey, ';'.join(wgs84))       
            for j in range(0, len(bd09)):
                oid += 1
                f_bd.write(str.format("{0},{1},{2}\n", oid, wgs84[j], bd09[j]))
            wgs84 = []

    f_bd.close()
    
    end = datetime.now()
    print(str.format("Completed. ({0})", end))
    print(str.format("Duration: {0}", end - start))
