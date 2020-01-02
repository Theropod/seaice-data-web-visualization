# seaice-data-web-visualization
 some demo scripts showing how to ready sea ice data for web visualization (Geojson only, no wms)
 
## 几种数据源 都以sea ice concentration为例：
全部都转成EPSG4326
### 模式 - netcdf
- CMIP6模式基本都有siconc
	/home3/synda/data/CMIP6/CMIP/NCAR/CESM2/historical/r1i1p1f1/SImon/siconc/gn/v20190308/siconc_SImon_CESM2_historical_r1i1p1f1_gn_185001-201412.nc 找了这一个作为例子。 185001-201412,1980个月。 但是用cdo remapbil没法插值到common grid, 显示结果只有全球的一部分有值。
- 换了`cdo remapbil,r360x180 -selvar,siconc siconc_SImon_CAMS-CSM1-0_historical_r1i1p1f1_gn_185001-201412.nc output.nc`反而就可以，原因不明。
- 重采样之后可能需要的各种处理
```
ncks -O --msa -d lon,181.,360. -d lon,0.,180.0 output.nc output2.nc #这个msa选项就非常神,最终把 180到360的部分移动到了-180到180
ncra -d time,1977,1979 output2.nc siconc2014.nc #提取2014后三个月平均
gdal_translate -srcwin 0 0 360 30 siconc2014.nc siconc2014reprojected.nc #只要北纬60-90
gdal_polygonize.py siconc2014reprojected.nc -f "GeoJSON" siconc2014reprojected.geojson
```
### 实测（船/走航）-  csv/geojson 等等
- https://icewatch.met.no/cruises?year=2014 下载的例子，因为有一个互动地图可以看，而且直接可以下载GEOJSON。但是他们组装geojson的时候把features里面多套了一层array,所以读不了，得手动改正。
### 遥感 -  hdf/tiff
- 选择例子 https://seaice.uni-bremen.de/start/data-archive/ 这里的AMSR2算出来的海冰密集度。官方提供了HDF4/TIFF/PNG预览
 - HDF4格式的附有一个二维数组位置和地球坐标的对照表 https://seaice.uni-bremen.de/data/grid_coordinates/ ，没有带上投影
 - TIFF直接可以在QGIS看，投影是EPSG 3411. 0-100表示concentration，120是陆地/missing
 - 标准数据都是6.25km的格网（分辨率太高了，需要降一点,要不然leaflet太卡）因此resample到4326下,0.25网格，而且只选取了北纬30度以上的区域
```
gdalwarp -t_srs EPSG:4326 -tr 0.25 0.25 -te -180 30 180 90 asi-AMSR2-n6250-20141201-v5.4.tif asi-AMSR2-n6250-20141201-v5.4.reprojected.tif
gdal_calc.py -A asi-AMSR2-n6250-20141201-v5.4.reprojected.tif --outfile=asi-AMSR2-n6250-20141201-v5.4.reprojected.mask.tif --calc="0*(A<0)+1*((A>0)*(A<=100))+0*(A==120)" --NoDataValue=0 #搞一个mask出来，最终只显示有冰的
gdal_polygonize.py asi-AMSR2-n6250-20141201-v5.4.reprojected.tif -mask asi-AMSR2-n6250-20141201-v5.4.reprojected.mask.tif -f "GeoJSON" asi-AMSR2-n6250-20141201-v5.4.reprojected.geojson -b 1 # 使用mask，转换geojson 最后不设置波段的话会得不到DN值
```
### 显示在地图上
用leaflet加载json。
主要复杂的地方在于定义了一个极地的投影，但大多数地图没有北极的瓦片。无奈照抄了一波emusat服务的瓦片

GeoSensorWebLab/polarmap.js或者可以用这个，不想看了

### 另外有关遥感和实测数据的对比
http://html.rhhz.net/ygxb/ygxb-21-3-zhaojiechen.htm
- 从2012年雪龙在北极航测的OBS-SIC海冰密集度与几种被动微波遥感PM-SIC数据对比结果看，德国用AMSR2卫星、ASI算法的数据偏差最小。
