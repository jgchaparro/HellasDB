# Hellas Database

![lefkada_banner](https://www.altitude.gr/wp-content/uploads/2020/09/banner-lefkada-oi-dekatreis-pio-ekpliktikes-paralies-tis-travel-altitudegr-1024x576.jpg)

The Hellas Database aims to gather population and other data from ELSTAT in a clean format, ready to perform data analysis and visualizations.

[Click here to see an interactive map of Greece based on this database](https://public.tableau.com/app/profile/jgchaparro/viz/Hellas_db_dashboard/Generaldashboard).

## Features

- Legal and real population for 13 500 + locations in Greece based on ELSTAT data.
- Region, decentralized administration, nomos (province), dimos (municipality) and minicipal unit of each location.   
- Coordinates for ~ 97,5 % of locations.
- Terrain information: urban/rural, plains/mountains.
- Administrative information during the application of the Kapodistrias plan (1998 - 2010).
- Other information: capital seats, islands, etc.


## Sources

- [ELSTAT](https://www.statistics.gr/2011-census-pop-hous)

## Main files

- `final_databases/hellas_db.csv`: final database.
- `final_databases/hellas_db.xlsx`: final database as an Excel spreadsheet.

## Steps taken

1. Downloading ELSTAT census for 1991, 2001 and 2011 years, as well as other documents for coordinates and terrain data.
1. Adding coordinates (`lat`, `long`) and altitude (`h`) for most location through several complex functions.
1. Incorporating terrain information (`astikotita`, `orinotita`).
1. Postprocessing to obtain information abour capital seats and other relevant data for analysis.
1. Generating an [interactive dashboard in Tableau](https://public.tableau.com/app/profile/jgchaparro/viz/Hellas_db_dashboard/Generaldashboard).

## Next steps

- Convert location names in Katharevousa Greek to Dimotiki Greek.
- Find coordinates for the last remaing 300 units without data.  
- Separate the capital columns (`edres_`) to form a new table.
- Generate a version using Latin characters instead of Greek letters to improve accesibility for non-Greek-speaking users.

## Technology Stack

In this project the following libraries were used:

![Pandas](https://img.shields.io/badge/Pandas-1.3.4-blue)
![Numpy](https://img.shields.io/badge/NumPy-1.21.4-white)
![requests](https://img.shields.io/badge/requests-2.26-blue)
![urllib](https://img.shields.io/badge/requests-2.26-white)
![PyMySQL](https://img.shields.io/badge/PyMySQL-8.0.27-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4.35-white)