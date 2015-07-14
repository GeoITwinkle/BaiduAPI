# -*- coding: utf-8 -*-

# Map Projection
# WGS84, GCJ02, BD09, and Web Mercator

# Requirement: Python 3.x
# Developer: Xiaoxing Qin@Sun Yat-sen University
# Acknowledgement: Code is converted and modified based on http://www.oschina.net/code/snippet_260395_39205
# License: Academic use only

import codecs, math
from datetime import datetime

PI = 3.14159265358979324
X_PI = 3.14159265358979324 * 3000.0 / 180.0

def Delta(lat, lon):
    # Krasovsky 1940
    # a = 6378245.0
    # 1/f = 298.3 (卫星椭球坐标投影到平面地图坐标系的投影因子)
    # b = a * (1 - f)
    # ee = (a^2 - b^2) / a^2 (椭球的偏心率)

    a = 6378245.0
    ee = 0.00669342162296594323

    dLat = TransformLatitude(lon - 105.0, lat - 35.0)
    dLon = TransformLongitude(lon - 105.0, lat - 35.0)
    radLat = lat / 180.0 * PI
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * PI)
    return {'lat': dLat, 'lon': dLon}
     
# WGS-84 to GCJ-02
def WGS84ToGCJ02(wgsLat, wgsLon):
    if OutOfChina(wgsLat, wgsLon):
        return {'lat': wgsLat, 'lon': wgsLon}

    d = Delta(wgsLat, wgsLon)
    return {'lat': wgsLat + d['lat'], 'lon': wgsLon + d['lon']}

# GCJ-02 to WGS-84 Estimate
def GCJ02ToWGS84_Estimate(gcjLat, gcjLon):
    if OutOfChina(gcjLat, gcjLon):
        return {'lat': gcjLat, 'lon': gcjLon}
     
    d = Delta(gcjLat, gcjLon)
    return {'lat': gcjLat - d['lat'], 'lon': gcjLon - d['lon']}

# GCJ-02 to WGS-84 Binary Limit
def GCJ02ToWGS84_Exact(gcjLat, gcjLon):
    initDelta = 0.01
    threshold = 0.000000001
    dLat = initDelta
    dLon = initDelta
    mLat = gcjLat - dLat
    mLon = gcjLon - dLon
    pLat = gcjLat + dLat
    pLon = gcjLon + dLon
    wgsLat = wgsLon = i = 0
    
    while (1):
        wgsLat = (mLat + pLat) / 2
        wgsLon = (mLon + pLon) / 2
        tmp = WGS84ToGCJ02(wgsLat, wgsLon)
        dLat = tmp['lat'] - gcjLat
        dLon = tmp['lon'] - gcjLon
        
        if abs(dLat) < threshold and abs(dLon) < threshold:
            break

        if dLat > 0:
            pLat = wgsLat
        else:
            mLat = wgsLat
                
        if dLon > 0:
            pLon = wgsLon
        else:
            mLon = wgsLon
        
        i += 1
        if i > 10000:
            break

    return {'lat': wgsLat, 'lon': wgsLon}

# GCJ-02 to BD-09
def GCJ02ToBD09(gcjLat, gcjLon):
    x = gcjLon
    y = gcjLat  
    z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * X_PI)  
    theta = math.atan2(y, x) + 0.000003 * math.cos(x * X_PI)  
    bdLon = z * math.cos(theta) + 0.0065  
    bdLat = z * math.sin(theta) + 0.006 
    return {'lat': bdLat, 'lon': bdLon}

# BD-09 to GCJ-02
def BD09ToGCJ02(bdLat, bdLon):
    x = bdLon - 0.0065
    y = bdLat - 0.006  
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * X_PI)  
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * X_PI)  
    gcjLon = z * math.cos(theta)  
    gcjLat = z * math.sin(theta)
    return {'lat': gcjLat, 'lon': gcjLon}

# WGS-84 to Web Mercator
def WGS84ToWebMercator(wgsLat, wgsLon):
    x = wgsLon * 20037508.34 / 180.0
    y = math.log(math.tan((90.0 + wgsLat) * PI / 360.0)) / (PI / 180.0)
    y = y * 20037508.34 / 180.0
    return {'lat': y, 'lon' : x}

    # if abs(wgsLon) > 180 or abs(wgsLat) > 90:
        # return None
    # x = 6378137.0 * wgsLon * 0.017453292519943295
    # a = wgsLat * 0.017453292519943295
    # y = 3189068.5 * math.log((1.0 + math.sin(a)) / (1.0 - math.sin(a)))
    # return {'lat': y, 'lon': x}

# Web Mercator to WGS-84
def WebMercatorToWGS84(mercatorLat, mercatorLon):
    x = mercatorLon / 20037508.34 * 180.0
    y = mercatorLat / 20037508.34 * 180.0
    y = 180.0 / PI * (2 * math.atan(math.exp(y * PI / 180.0)) - PI / 2.0)
    return {'lat': y, 'lon' :x}
    
    # if abs(mercatorLon) < 180 and abs(mercatorLat) < 90:
        # return None
    # if abs(mercatorLon) > 20037508.3427892 or abs(mercatorLat) > 20037508.3427892:
        # return None
    # a = mercatorLon / 6378137.0 * 57.295779513082323
    # x = a - (math.floor(((a + 180.0) / 360.0)) * 360.0)
    # y = (1.5707963267948966 - (2.0 * math.atan(math.exp((-1.0 * mercatorLat) / 6378137.0)))) * 57.295779513082323
    # return {'lat': y, 'lon': x}

# Two point's distance
def Distance(latA, lonA, latB, lonB):
    earthR = 6371000.0
    x = math.cos(latA * PI / 180.0) * math.cos(latB * PI / 180.0) * math.cos((lonA - lonB) * PI / 180.0)
    y = math.sin(latA * PI / 180.0) * math.sin(latB * PI / 180.0)
    s = x + y
    if s > 1:
            s = 1
    if s < -1:
            s = -1
    alpha = math.acos(s)
    distance = alpha * earthR
    return distance

def OutOfChina(lat, lon):
    return not (72.004 <= lon <= 137.8347 and 0.8293 <= lat <= 55.8271)

def TransformLatitude(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * PI) + 40.0 * math.sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * PI) + 320 * math.sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret

def TransformLongitude(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 * math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * PI) + 40.0 * math.sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * PI) + 300.0 * math.sin(x / 30.0 * PI)) * 2.0 / 3.0
    return ret

if __name__ == '__main__':
    # General test
    print(str.format("{0}\t{1: >20}\t{2: >20}", "System", "Latitude", "Longitude"))
    
    wgs84 = {'lat': 23, 'lon': 113}
    print(str.format("WGS84\t{0: >20}\t{1: >20}", wgs84['lat'], wgs84['lon']))
    
    gcj02 = WGS84ToGCJ02(wgs84['lat'], wgs84['lon'])
    print(str.format("GCJ02\t{0: >20}\t{1: >20}", gcj02['lat'], gcj02['lon']))
    
    bd09 = GCJ02ToBD09(gcj02['lat'], gcj02['lon'])
    print(str.format("BD09\t{0: >20}\t{1: >20}", bd09['lat'], bd09['lon']))

    gcj02_rev = BD09ToGCJ02(bd09['lat'], bd09['lon'])
    print(str.format("GCJ02\t{0: >20}\t{1: >20}", gcj02_rev['lat'], gcj02_rev['lon']))
    
    wgs84_rev = GCJ02ToWGS84_Exact(gcj02_rev['lat'], gcj02_rev['lon'])
    print(str.format("WGS84\t{0: >20}\t{1: >20}", wgs84_rev['lat'], wgs84_rev['lon']))

    wm = WGS84ToWebMercator(wgs84['lat'], wgs84['lon'])
    print(str.format("WebMc\t{0: >20}\t{1: >20}", wm['lat'], wm['lon']))
    
    wgs84_rev = WebMercatorToWGS84(wm['lat'], wm['lon'])
    print(str.format("WGS84\t{0: >20}\t{1: >20}", wgs84_rev['lat'], wgs84_rev['lon']))

    # Precision test
    start = datetime.now()
    print(str.format("Precision Test ({0})", start))
    
    f_in = codecs.open("Input/Projection.csv", "r", encoding = "utf-8-sig").readlines()
    f_out = codecs.open("Output/Projection Test.csv", "w", encoding = "utf-8-sig")
    f_out.write("OBJECTID,X_WGS84,Y_WGS84,X_BD09,Y_BD09,X_WGS84_Exact,Y_WGS84_Exact,Distance_Exact,X_WGS84_Reg,Y_WGS84_Reg,Distance_Reg\n")

    for r in f_in[1:]:
        r = r.strip().split(',')

        x_wgs84 = float(r[1])
        y_wgs84 = float(r[2])
        x_bd09 = float(r[3])
        y_bd09 = float(r[4])

        # Convert by functions
        gcj02 = BD09ToGCJ02(y_bd09, x_bd09)
        wgs84 = GCJ02ToWGS84_Exact(gcj02['lat'], gcj02['lon'])
        x_wgs84_exact = float(wgs84['lon'])
        y_wgs84_exact = float(wgs84['lat'])

        # Convert by regression (Guangzhou)
        y_wgs84_reg = -0.0398742657492583 + 0.000368742795507935 * x_bd09 + 0.999770842271639 * y_bd09
        x_wgs84_reg = -0.081774703936586 + 1.00062621134481 * x_bd09 - 0.0000472322372012116 * y_bd09

        # Calculate distance
        d_exact = Distance(y_wgs84_exact, x_wgs84_exact, y_wgs84, x_wgs84)
        d_reg = Distance(y_wgs84_reg, x_wgs84_reg, y_wgs84, x_wgs84)

        f_out.write(str.format("{0},{1},{2},{3},{4},{5},{6}\n", ','.join(r), x_wgs84_exact, y_wgs84_exact, d_exact, x_wgs84_reg, y_wgs84_reg, d_reg))
        
    f_out.close()

    end = datetime.now()
    print(str.format("Completed ({0})", start))
    print(str.format("Duration: {0}", end - start))

