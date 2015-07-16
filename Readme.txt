Baidu API Instruction
Xiaoxing Qin

1. Before running APIs, configure required files in Config folder
API		Requirement			Configuration
ALL		API Key.csv			If not your Baidu API key, replace with your key
Coordinate	Coordinate System.csv		Do NOT modify
Geocoding	City.csv			If not listed, record the NAME of your specific city
Locator		City.csv			If not listed, record the NAME and CODE of your specific city
Place		City.csv			If not listed, record the NAME and EXTENT (WGS84 coordinates of lower-left and upper-right rectangle) of your specific city

2. Format and store your input files in Input folder, output and error (optional) files are in Output folder
API		Input				Output				Error (Optional)
Coordinate	Origin Coordinate.csv		Projected Coordinate.csv	N/A
Geocoding	Address.csv			Geocoded Address.csv		Geocoding Error.csv
Locator		Ungeocoded Address.csv		Located Address.csv		Locating Error.csv
Place		N/A				{City}_{POI}.csv		N/A

3. Run the script and configure parameters on screen

Any questions, e-mail to Xiaoxing.Qin@gmail.com