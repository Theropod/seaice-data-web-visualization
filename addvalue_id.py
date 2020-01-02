import json

inputGeojson='./asi-AMSR2-n6250-20141201-v5.4.reprojected.geo.json'
outputGeojson='asi-AMSR2-n6250-20141201-v5.4.reprojected_values.geo.json'
with open(inputGeojson, 'r') as f:
    gdal_json = json.load(f)

i=0
for feature in gdal_json["features"]:
    feature["id"]=i
    i+=1
    feature["value"]=feature["properties"]["DN"]

with open(outputGeojson, 'w') as f:
    json.dump(gdal_json,f)