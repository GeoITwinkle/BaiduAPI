Baidu API Repository
===========

#### Service Provider
Baidu, Inc.

#### Reference
http://developer.baidu.com/map/index.php?title=webapi

#### Developer
Xiaoxing Qin@Sun Yat-sen University

#### Contact
Xiaoxing.Qin@gmail.com

#### Acknowledgement
* Kejing Peng@Microsoft (https://github.com/pkkj)
* Open source code@http://www.oschina.net/code/snippet_260395_39205

#### License

Academic use only

#### Requirement

Python 3.x

#### Description

API	|	File			|	Use
------------- | -------------|-------------
Coordinate| 	Baidu Coordinate API.py	| 	Convert coordinate systems
Geocoding| 	Baidu Geocoding API.py	| 	Geocode addresses
Locator	| 	Baidu Locator API.py	| 	Locate addresses that cannot be geocoded by Geocoding API
Place	| 	Baidu Place API.py	| 	Get POI data

#### Instruction
1 . Before running APIs, configure required files in Config folder

API	|	Requirement		|	Configuration
------------- | -------------|-------------
ALL	|	API Key.csv	|		If not your Baidu API key, replace with your key
Coordinate|	Coordinate System.cfg	|	Do NOT modify
Geocoding |	City.csv	|		If not listed, record the NAME of your specific city
Locator	|	City.csv	|		If not listed, record the NAME and CODE of your specific city
Place	|	City.csv	|		If not listed, record the NAME and EXTENT (WGS84 coordinates of lower-left and upper-right rectangle) of your specific city

2 . Format and store your input files in Input folder, output and error (optional) files are in Output folder

API	|	Input		|		Output		|		Error (Optional)
------------- | -------------|------------- | ---------------
Coordinate |	Origin Coordinate.csv	|	Projected Coordinate.csv|	N/A
Geocoding	| Address.csv		|	Geocoded Address.csv	|	Geocoding Error.csv
Locator	|	Ungeocoded Address.csv	|	Located Address.csv	|	Locating Error.csv
Place	|	N/A		|		{City}_{POI}.csv	|	N/A

3 . Run the script and configure parameters on screen
