# Hellas Database

![lefkada_banner](https://www.altitude.gr/wp-content/uploads/2020/09/banner-lefkada-oi-dekatreis-pio-ekpliktikes-paralies-tis-travel-altitudegr-1024x576.jpg)

The Hellas Database aims to gather population data from ELSTAT census and other sources in a clean format, ready to perform data analysis and visualizations.

## Features

- Legal and real population for 13 000+ locations in Greece based on ELSTAT data.
- Location names in dimotiki Greek.
- All administrative units a location belongs to.   
- Coordinates for ~ 70 % of locations.
- Mean temperature for locations with coordinates available.

## Sources

- [ELSTAT](https://www.statistics.gr/2011-census-pop-hous)
- [GeoNames API](http://www.geonames.org/export/web-services.html)
- [OpenWeather API](https://openweathermap.org/api/statistics-api)

## Files

- `data/hellas_db.csv`: final database.
- `data/geonames_df.csv`: web-scapred data for all perifereies from Geonames.

## Steps taken

1. Downloading ELSTAT census for 1991, 2001 and 2011 years.
1. Cleaning census data. Conversion of katharevousa nomenclature to dimotiki.
1. Getting area data for all 13 perifereies and all available population registers for each perifereia through Geonames API.
1. Joining Geonames API data in a unique database.
1. Joining census and Geonames data based on town name (`desc`) and province (`nomos`) to obtain coordinates for each location.
1. Obtaining mean temperature data through OpenWeather API.

## Caveats

- Conversion from katharevousa to dimotiki nomenclature might not be completely accurate. Some specific conversion rules for relevant population clusters were added to make up for this, but coordinates for smaller populations might be lost due to incorrect conversion. 
- To avoid discrepancies during census and Geonames databases merging, some locations were given an approximate `nomos` based on the available information.
- Due to the frequent duplicated name towns in the same province, it is impossible to assign coordinates to some locations on a systematic basis.

## Technology Stack

In this project the following libraries were used:

![Pandas](https://img.shields.io/badge/Pandas-1.3.4-blue)
![Numpy](https://img.shields.io/badge/NumPy-1.21.4-white)
![requests](https://img.shields.io/badge/requests-2.26-blue)
![urllib](https://img.shields.io/badge/requests-2.26-white)
![PyMySQL](https://img.shields.io/badge/PyMySQL-8.0.27-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4.35-white)