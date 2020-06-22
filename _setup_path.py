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
import numpy as np

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

## US election analysis begins
(
    np.array(
        df_election_pres[
            df_election_pres.FIPS == 1001
        ][
            df_election_pres.party == 'republican'
        ].candidatevotes
    ) / np.array(
        df_election_pres[
            df_election_pres.FIPS == 1001
        ][
            df_election_pres.party == 'republican'
        ].totalvotes
    )
).mean() * 100.00
## US COVID data analysis
df_covid = (
    df_covid_dead[df_covid_dead.FIPS > 1000]
)[df_covid_dead.FIPS < 80000]  # This FIPS lies in US voting counties
days_since_first_death = \
    (
        (
            np.where(
                df_covid_dead[
                    df_covid_dead.FIPS == 1067
                ].values[0][12:] > 0
            )
        )[0][-1] - (
            np.where(
                df_covid_dead[
                    df_covid_dead.FIPS == 1067
                ].values[0][12:] > 0
            )
        )[0][0]
    )

