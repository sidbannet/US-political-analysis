## Import system tools
import os
import subprocess
import sys

## Setup path correctly
repo_dir = subprocess.check_output(
    'git rev-parse --show-toplevel', shell=True,
).decode('utf-8').strip()
sys.path.insert(0, repo_dir + os.sep + 'stat-tools')
##
import pandas as pd

##
df_covid_dead = pd.DataFrame()
df_election_pres = pd.DataFrame()
##
us_data_folder = r'COVID-19' \
    + os.sep + 'csse_covid_19_data' \
    + os.sep + 'csse_covid_19_time_series' \
    + os.sep
us_election_folder = r'US-election-data' + os.sep
##
df_covid_dead = pd.read_csv(
    us_data_folder + 'time_series_covid19_deaths_US.csv',
)
##
df_election_pres = pd.read_csv(
    us_election_folder + 'countypres_2000-2016.csv',
)
