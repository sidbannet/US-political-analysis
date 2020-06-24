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
df_covid_conf = pd.read_csv(
    us_data_folder + 'time_series_covid19_confirmed_US.csv'
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
##

var_repub = ((
          df_election_pres[
              df_election_pres.FIPS == 1001
              ][
              df_election_pres.year == 2016
              ][
              df_election_pres.party == 'republican'
              ].candidatevotes
      ) / (
          df_election_pres[
              df_election_pres.FIPS == 1001
              ][
              df_election_pres.year == 2016
              ][
              df_election_pres.party == 'republican'
              ].totalvotes
      )).values[0] * 100

var_dem = ((
          df_election_pres[
              df_election_pres.FIPS == 1001
              ][
              df_election_pres.year == 2016
              ][
              df_election_pres.party == 'democrat'
              ].candidatevotes
      ) / (
          df_election_pres[
              df_election_pres.FIPS == 1001
              ][
              df_election_pres.year == 2016
              ][
              df_election_pres.party == 'democrat'
              ].totalvotes
      )).values[0] * 100

## US COVID data analysis
df_covid = (
    df_covid_dead[df_covid_dead.FIPS > 1000]
)[df_covid_dead.FIPS < 80000]  # This FIPS lies in US voting counties
df_conf = (
    df_covid_conf[df_covid_conf.FIPS > 1000]
)[df_covid_conf.FIPS < 80000]
##
days = []
days_conf = []
for index, row in df_covid.iterrows():
    days.append(
        np.where(
            row.values[12:] > 0
        )[0].size
    )
for index, row in df_conf.iterrows():
    days_conf.append(
        np.where(
            row.values[11:] > 5
        )[0].size
    )

##
import matplotlib.pyplot as plt
##
affected = np.zeros_like(df_covid.values[0][12:])
population = np.zeros_like(df_covid.values[0][12:])
confirmed = np.zeros_like(df_conf.values[0][11:])
confirmed_population = np.zeros_like(df_conf.values[0][11:])
##
fig = plt.figure()
ax = fig.subplots()
for idx, row in df_covid.iterrows():
    try:
        if days[idx] == 0:
            continue
        else:
            x = np.array(
                np.linspace(start=0, stop=days[idx] - 1, num=days[idx]))
    except IndexError:
        continue
    try:
        ax.plot(x, row.values[-days[idx]:] / row.Population * 1e6, '-k')
        affected[:days[idx]] += row.values[-days[idx]:]
        population[:days[idx]] += row.Population
    except ValueError:
        pass
    except IndexError:
        pass
ax.set_yscale('log')
ax.plot(affected[:max(days) - 1] / population[:max(days) - 1] * 1e6, '-g',
        label='Mean')
##
fig = plt.figure()
ax = fig.subplots()
for idx, row in df_conf.iterrows():
    try:
        if days_conf[idx] == 0:
            continue
        else:
            x = np.array(
                np.linspace(start=0, stop=days[idx] - 1, num=days_conf[idx]))
    except IndexError:
        continue
    try:
        ax.plot(
            x,
            row.values[-days_conf[idx]:]
            / df_covid.Population.values[idx] * 1e6,
            '-k')
        confirmed[:days_conf[idx]] += row.values[-days_conf[idx]:]
        confirmed_population[:days_conf[idx]] += \
            df_covid.Population.values[idx]
    except ValueError:
        pass
    except IndexError:
        pass
ax.set_yscale('log')
ax.plot(
    confirmed[
        :max(days_conf) - 1
        ] / confirmed_population[
        :max(days_conf) - 1
        ] * 1e6,
    '-g',
    label='Mean'
)
##
covid_mat = []
covid_rel = []
covid_meas = []
conf_meas = []
electionbias = []
FIPS = []
lat = []
lon = []
for idx, row in df_covid.iterrows():
    FIPS.append(row.FIPS)
    lat.append(row.Lat)
    lon.append(row.Long_)
    if row.values[-1] == 0:
        covid_mat.append(0)
        covid_rel.append(0)
        covid_meas.append(0)
        electionbias.append(101)
        conf_meas.append(0)
        continue
    elif days[idx] == 0:
        covid_mat.append(0)
        covid_rel.append(0)
        covid_meas.append(0)
        electionbias.append(101)
        conf_meas.append(0)
        continue
    else:
        pass
    covid_mat.append(
        (row.values[-1] * 1e6) / (row.Population * days[idx])
    )
    covid_rel.append(
        ((row.values[-1] * 1e6) / row.Population) /
        ((affected[days[idx] - 1] * 1e6) / population[days[idx] - 1])
    )
    if days[idx] <= 80:
        covid_meas.append(
            ((row.values[-1] * 1e6) / row.Population) /
            ((affected[days[idx]] * 1e6) / population[days[idx]])
        )
    else:
        covid_meas.append(
            ((row.values[80 - 1] * 1e6) / row.Population) /
            ((affected[80 - 1] * 1e6) / population[80 - 1])
        )
    if days_conf[idx] <= 80:
        conf_meas.append(
            ((df_conf.values[idx][-1] * 1e6) / df_covid.Population.values[idx])
            / ((confirmed[days_conf[idx]] * 1e6)
               / confirmed_population[days_conf[idx]])
        )
    else:
        conf_meas.append(
            ((df_conf.values[idx][80 - 1] * 1e6)
             / df_covid.Population.values[idx]) /
            ((confirmed[80 - 1] * 1e6) / confirmed_population[80 - 1])
        )
    try:
        var_repub = (
            (
                df_election_pres[
                    df_election_pres.FIPS == row.FIPS
                ][
                    df_election_pres.year == 2016
                ][
                    df_election_pres.party == 'republican'
                ].candidatevotes
            ) / (
                df_election_pres[
                    df_election_pres.FIPS == row.FIPS
                ][
                    df_election_pres.year == 2016
                ][
                    df_election_pres.party == 'republican'
                ].totalvotes
            )
        ).values[0] * 100
        var_dem = (
            (
                df_election_pres[
                    df_election_pres.FIPS == row.FIPS
                ][
                    df_election_pres.year == 2016
                ][
                    df_election_pres.party == 'democrat'
                ].candidatevotes
            ) / (
                    df_election_pres[
                        df_election_pres.FIPS == row.FIPS
                    ][
                        df_election_pres.year == 2016
                    ][
                        df_election_pres.party == 'democrat'
                    ].totalvotes
            )
        ).values[0] * 100
    except IndexError:
        var_repub = 101
        var_dem = 0
    electionbias.append(
        var_repub - var_dem
    )
##
df_analysis = pd.DataFrame(index=FIPS)
df_analysis['death'] = covid_meas
df_analysis['conf'] = conf_meas
df_analysis['pop'] = df_covid.Population.values
df_analysis['elect'] = electionbias
df_analysis['long'] = lon
df_analysis['lat'] = lat
##
plt.scatter(
    electionbias, covid_meas, s=df_covid.Population.values / 10000, c=days)
plt.yscale('log')
plt.xlim(-100, 100)
plt.grid(True)
plt.ylim(0.001, 100)
plt.colorbar()
##
plt.scatter(
    df_analysis.elect, df_analysis.conf,
    s=df_covid.Population.values / 10000,
    c=days)
plt.yscale('log')
plt.xlim(-100, 100)
plt.grid(True)
plt.ylim(0.001, 100)
plt.colorbar()
