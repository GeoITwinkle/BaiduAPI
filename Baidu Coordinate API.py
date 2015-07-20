# -*- coding: utf-8 -*-

# Baidu Coordinate Converter

# Service Provider: Baidu, Inc.
# Developer: Xiaoxing Qin@Sun Yat-sen University
# Acknowledgement: Kejing Peng@Microsoft provided instructions
# License: Academic use only
# Requirement: Python 3.x

import urllib.request, json, codecs, os, sys, traceback, MapProjection
from datetime import datetime

# Convert to B009 (Degree or Meter)
def ConvertToBD09(apikey, f_in, f_out, ocs_id, pcs_id):
    i = oid = 0
    oc = []

    fl = f_in.readlines()
    for f in fl[1:]:
        i += 1
        r = f.strip().split(',')
        oc.append(','.join(r[1:]))
        
        if i % 100 == 0 or i == len(fl) - 1:          
            url = str.format("http://api.map.baidu.com/geoconv/v1/?&ak={0}&from={1}&to={2}&coords={3}", apikey, ocs_id, pcs_id, ';'.join(oc))
            print(url)
            data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))

            if 'result' in data:
                for r in data['result']:                    
                    oid += 1
                    j = oid % 100 - 1
                    f_out.write(str.format("{0},{1},{2},{3}\n", oid, oc[j], r['x'], r['y']))

            oc = []

    f_in.close()
    f_out.close()

# Convert coordinates
def Process(apikey, cs, ocs_id, pcs_id):
    try:
        start = datetime.now()
        print(str.format("Converting {0} to {1} ({2})", cs[ocs_id], cs[pcs_id], start))

        f_in = codecs.open("Input/Origin Coordinate.csv", "r", encoding = "utf-8-sig")
        f_out = codecs.open("Output/Temp.csv", "w", encoding = "utf-8-sig")    
        f_out.write("OBJECTID,X_Origin,Y_Origin,X_Projected,Y_Projected\n")
    
        if pcs_id in ["5", "6"]:
            ConvertToBD09(apikey, f_in, f_out, ocs_id, pcs_id)

            if os.path.exists("Output/Projected Coordinate.csv"):
                os.remove("Output/Projected Coordinate.csv")
            os.rename("Output/Temp.csv", "Output/Projected Coordinate.csv")
        elif pcs_id in ["1", "3"]:
            fl = None
            f_out_new = codecs.open("Output/Projected Coordinate.csv", "w", encoding = "utf-8-sig")    
            f_out_new.write("OBJECTID,X_Origin,Y_Origin,X_Projected,Y_Projected\n")        

            if ocs_id == "5":
                fl = f_in.readlines()
                f_out.close()
            else:
                ConvertToBD09(apikey, f_in, f_out, ocs_id, "5")
                f_in_new = codecs.open("Output/Temp.csv", "r", encoding = "utf-8-sig")
                fl = f_in_new.readlines()

            for f in fl[1:]:            
                r = f.strip().split(',')
                [x_bd09, y_bd09] = map(lambda x: float(x), r[1:3] if ocs_id == "5" else r[3:])           
                gcj02 = MapProjection.BD09ToGCJ02(y_bd09, x_bd09)
                
                x = y = 0
                if pcs_id == "1":                
                    wgs84 = MapProjection.GCJ02ToWGS84_Exact(gcj02['lat'], gcj02['lon'])
                    x = wgs84['lon']
                    y = wgs84['lat']                
                else:
                    x = gcj02['lon']
                    y = gcj02['lat']
                f_out_new.write(str.format("{0},{1},{2}\n", ','.join(r[:3]), x, y))
                
            os.remove("Output/Temp.csv")
        else:
            raise Exception
        
        end = datetime.now()
        print(str.format("Completed ({0})", end))
        print(str.format("Duration: {0}", end - start))

    except:
        msg = traceback.format_exc()
        print("Error:\n" + msg)
        
if __name__ == '__main__':
    # Configuration
    print("========== Configuration ==========")
    
    f_key = codecs.open("Config/API Key.csv", "r", encoding = "utf-8-sig")
    apikey = f_key.readlines()[1].strip().split(',')[1]
    f_key.close()

    url = str.format("http://api.map.baidu.com/geoconv/v1/?&ak={0}&from=1&to=5&coords=113,23", apikey)
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
    if data['status'] != 0:
        print("Invalid API key.")
        sys.exit(1)
        
    cs = {}
    f_cs = codecs.open("Config/Coordinate System.cfg", "r", encoding = "utf-8-sig")
    for f in f_cs.readlines()[1:]:
        r = f.strip().split(',')
        cs[r[0]] = r[1]
    f_cs.close()
    
    # Select coordinate system   
    print("ID\tInput Coordinate System")
    for ocs in sorted(cs):
        print(str.format("{0}\t{1}", ocs, cs[ocs]))    

    ocs_id = input("ID of input coordinate system: ")
    if ocs_id not in cs:
        print("Error: Incorrect ID.")
        sys.exit(1)        
    print()
    
    pcs_ids = list(filter(lambda x: x != ocs_id, ["1", "3", "5", "6"]))
    print("ID\tOutput Coordinate System")
    for pcs in pcs_ids:
        print(str.format("{0}\t{1}", pcs, cs[pcs]))

    pcs_id = input("ID of output coordinate system: ")
    if pcs_id not in pcs_ids:
        print("Error: Incorrect ID.")
        sys.exit(1)
    
    # Convert coordinates
    print("========== Process ==========")
    Process(apikey, cs, ocs_id, pcs_id) 
