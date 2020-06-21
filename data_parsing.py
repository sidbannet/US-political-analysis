## Load packages
import os
import pandas as pd
import numpy as np

## Initialize
df_covid_dead = pd.DataFrame()
df_election_pres = pd.DataFrame()
## Folder path defined
us_data_folder = r'COVID-19' \
    + os.sep + 'csse_covid_19_data' \
    + os.sep + 'csse_covid_19_time_series' \
    + os.sep
us_election_folder = r'US-election-data' + os.sep
## COVID US death record added
df_covid_dead = pd.read_csv(
    us_data_folder + 'time_series_covid19_deaths_US.csv',
)
## Election data record added
df_election_pres = pd.read_csv(
    us_election_folder + 'countypres_2000-2016.csv',
)

