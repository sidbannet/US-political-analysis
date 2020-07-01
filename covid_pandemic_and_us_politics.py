# -*- coding: utf-8 -*-

## Import common packages and modules
import os
import subprocess
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.figure_factory as ff

## Setup path correctly
repo_dir = subprocess.check_output(
    'git rev-parse --show-toplevel', shell=True,
).decode('utf-8').strip()
sys.path.insert(0, repo_dir + os.sep + 'stat-tools')

## Import repo specific modules
from sbstat.tool.analysis import ProbabilityDensity as Pd


## Initialize pandas
df_covid_dead = pd.DataFrame()
df_election_pres = pd.DataFrame()
## Define folder
us_data_folder = r'COVID-19' \
                 + os.sep + 'csse_covid_19_data' \
                 + os.sep + 'csse_covid_19_time_series' \
                 + os.sep
us_election_folder = r'US-election-data' + os.sep
## Read COVID data
df_covid_dead = pd.read_csv(
    us_data_folder + 'time_series_covid19_deaths_US.csv',
)
df_covid_conf = pd.read_csv(
    us_data_folder + 'time_series_covid19_confirmed_US.csv'
)
## Read election data
df_election_pres = pd.read_csv(
    us_election_folder + 'countypres_2000-2016.csv',
)
## Read Income data
df_income = pd.read_csv(
    us_election_folder + 'SAIPESNC_28JUN20_23_12_20_62.csv',
)


## US COVID data analysis
df_covid = (
    df_covid_dead[df_covid_dead.FIPS > 1000]
)[df_covid_dead.FIPS < 80000].copy()  # This FIPS lies in US voting counties
df_conf = (
    df_covid_conf[df_covid_conf.FIPS > 1000]
)[df_covid_conf.FIPS < 80000].copy()
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


affected = np.zeros_like(df_covid.values[0][12:])
population = np.zeros_like(df_covid.values[0][12:])
confirmed = np.zeros_like(df_conf.values[0][11:])
confirmed_population = np.zeros_like(df_conf.values[0][11:])


##
fig = plt.figure('COVID trajectory plots')
ax = fig.subplots(nrows=2, ncols=1)
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
        ax[0].plot(x, row.values[-days[idx]:] / row.Population * 1e6,
                '-k', label=row.FIPS)
        affected[:days[idx]] += row.values[-days[idx]:]
        population[:days[idx]] += row.Population
    except ValueError:
        pass
    except IndexError:
        pass
ax[0].plot(affected[:max(days) - 1] / population[:max(days) - 1] * 1e6, '-g',
        label='Mean')
_ = ax[0].set_title('Deaths')

for idx, row in df_conf.iterrows():
    try:
        if days_conf[idx] == 0:
            continue
        else:
            x = np.array(
                np.linspace(start=0, stop=days_conf[idx] - 1, num=days_conf[idx]))
    except IndexError:
        continue
    try:
        ax[1].plot(
            x,
            row.values[-days_conf[idx]:]
            / df_covid.Population.loc[idx] * 1e6,
            '-k',
            label=row.FIPS)
        confirmed[:days_conf[idx]] += row.values[-days_conf[idx]:]
        confirmed_population[:days_conf[idx]] += \
            df_covid.Population.loc[idx]
    except ValueError:
        pass
    except IndexError:
        pass
ax[1].plot(
    confirmed[
        :max(days_conf)
        ] / confirmed_population[
        :max(days_conf)
        ] * 1e6,
    '-g',
    label='Mean'
)
_ = ax[1].set_title('Confirmed')
_ = [axes.grid(True) for axes in ax.flat]
_ = [axes.set_yscale('log') for axes in ax.flat]
_ = [axes.set_ylim(1, 1e8) for axes in ax.flat]
_ = ax[-1].set_xlabel('Number of days [#]')
_ = fig.suptitle('COVID trajectory')


days_upper_threshold = 110
covid_mat = []
covid_rel = []
covid_meas = []
conf_meas = []
electionbias = []
mor_rate = []
growth_rate = []
FIPS = []
lat = []
lon = []
poverty = []
income = []
first_wave = []
for idx, row in df_covid.iterrows():
    if df_conf.loc[idx].values[-1] == 0:
        mor_rate.append(0)
        growth_rate.append(0)
        first_wave.append(0)
    else:
        mor_rate.append(row.values[-1] / df_conf.loc[idx].values[-1])
        if df_conf.loc[idx].values[-11] == 0:
            growth_rate.append(-1)
        else:
            growth_rate.append(
                df_conf.loc[idx].values[-1] /
                df_conf.loc[idx].values[-11]
            )
        try:
            first_death_day = np.where(
                row.values[12:] > 0
            )[0][0]
            first_wave.append(
                df_conf.loc[idx].values[
                    12 + first_death_day + 10
                ] / df_conf.loc[idx].values[
                    12 + first_death_day
                ]
            )
        except IndexError:
            first_wave.append(-1)
    FIPS.append(row.FIPS)
    lat.append(row.Lat)
    lon.append(row.Long_)
    try:
        var = (
            (
                df_election_pres[
                    df_election_pres.FIPS == row.FIPS
                ][
                    df_election_pres.year == 2016
                ][
                    df_election_pres.party == 'republican'
                ].candidatevotes.values[0] -
                df_election_pres[
                    df_election_pres.FIPS == row.FIPS
                ][
                    df_election_pres.year == 2016
                ][
                    df_election_pres.party == 'democrat'
                ].candidatevotes.values[0]
            ) / (
                df_election_pres[
                    df_election_pres.FIPS == row.FIPS
                ][
                    df_election_pres.year == 2016
                ][
                    df_election_pres.party == 'republican'
                ].totalvotes.values[0]
            )
        )* 100        
    except IndexError:
        var = 101
    electionbias.append(
        var
    )
    try:
        var = float(
            (df_income[
               df_income[
                    'County ID'
                ] == row.FIPS
            ][
                'Median Household Income in Dollars'
            ].astype(str)
            ).values[0].strip('$').replace(',', '')
        )
    except IndexError:
        var = 0
    income.append(var)
    try:
        var = float(
            (df_income[
               df_income[
                    'County ID'
                ] == row.FIPS
            ][
                'All Ages in Poverty Percent'
            ].astype(str)
            ).values[0].strip('$').replace(',', '')
        )
    except IndexError:
        var = 0
    poverty.append(var)
    if row.values[-1] == 0:
        covid_mat.append(0)
        covid_rel.append(0)
        covid_meas.append(0)
        conf_meas.append(0)
        continue
    elif days[idx] == 0:
        covid_mat.append(0)
        covid_rel.append(0)
        covid_meas.append(0)
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
    if days[idx] <= days_upper_threshold:
        covid_meas.append(
            ((row.values[-1] * 1e6) / row.Population) /
            ((affected[days[idx]] * 1e6) / population[days[idx]])
        )
    elif days[idx] < 10:
        covid_mat.append(0)
        covid_rel.append(0)
        covid_meas.append(0)        
        conf_meas.append(0)
    else:
        covid_meas.append(
            ((row.values[days_upper_threshold - 1] * 1e6) / row.Population) /
            ((affected[days_upper_threshold - 1] * 1e6) / population[days_upper_threshold - 1])
        )
    if days_conf[idx] <= days_upper_threshold:
        conf_meas.append(
            ((df_conf.loc[idx].values[-1] * 1e6) / df_covid.Population.loc[idx])
            / ((confirmed[days_conf[idx]] * 1e6)
               / confirmed_population[days_conf[idx]])
        )
    elif days_conf[idx] < 10:
        conf_meas.append(0)
    else:
        conf_meas.append(
            ((df_conf.loc[idx].values[110 - 1] * 1e6)
             / df_covid.Population.loc[idx]) /
            ((confirmed[days_upper_threshold - 1] * 1e6) / confirmed_population[days_upper_threshold - 1])
        )

##
df_analysis = pd.DataFrame(index=FIPS)
df_analysis.index.name = 'FIPS'
df_analysis['Death'] = covid_meas
df_analysis['Conf'] = conf_meas
df_analysis['Mortality'] = mor_rate
df_analysis['Growth'] = growth_rate
df_analysis['Election'] = electionbias
df_analysis['Income'] = income
df_analysis['Poverty'] = poverty
df_analysis['SecondWave'] = np.divide(growth_rate, first_wave)
df_analysis['Population'] = df_covid.Population.values
df_analysis['Days'] = days_conf
df_analysis['Long'] = lon
df_analysis['Lat'] = lat
df_analysis['County'] = df_covid.Combined_Key.values
df_analysis['State'] = df_covid.Province_State.values
df_analysis['UID'] = df_covid.UID.values

(df_analysis[df_analysis.Population > 1000][df_analysis.State == 'California']).sort_values(
    by=['Growth', 'SecondWave', 'Death', 'Mortality', 'Conf'],
    axis=0, ascending=False, ignore_index=False).head(20)

fig = plt.figure('US politics and COVID')
ax = fig.subplots(ncols=4, sharex=True, sharey=False)
ax[0].scatter(
    df_analysis.Election, df_analysis.Death,
    s=df_analysis.Population.values / 10000, c=df_analysis.Days)
ax[0].set_xlim(-100, 100)
ax[1].scatter(
    df_analysis.Election, df_analysis.Conf,
    s=df_analysis.Population.values / 10000,
    c=days_conf)
ax[2].scatter(
    df_analysis.Election, df_analysis.Growth,
    s=df_analysis.Population.values / 10000,
    c=days_conf)
ax[3].scatter(
    df_analysis.Election, df_analysis.Mortality,
    s=df_analysis.Population.values / 10000,
    c=days_conf)
_ = [axes.grid(True) for axes in ax.flat]
ax[0].set_yscale('log')
ax[1].set_yscale('log')
ax[2].set_yscale('linear')
ax[3].set_yscale('linear')
_ = [axes.set_xlabel('Political bias') for axes in ax.flat]
ax[0].set_ylabel('COVID metric')
ax[0].set_title('COVID Deaths vs. Politics')
ax[1].set_title('COVID Cases vs. Politics')
ax[2].set_title('COVID Growth vs. Politics')
ax[3].set_title('COVID Mortality vs. Politics')
_ = fig.suptitle('US county COVID and Political preference')
_ = [axes.set_ylim(0.001, 100) for axes in ax.flat]
ax[2].set_ylim(0.5, 5)
ax[3].set_ylim(0.0, 0.2)
fig.set_size_inches(w=18, h=6)
fig.tight_layout(pad=3)

fig = plt.figure('US Income and COVID')
ax = fig.subplots(ncols=4, sharex=True, sharey=False)
ax[0].scatter(
    df_analysis.Income, df_analysis.Death,
    s=df_analysis.Population.values / 10000, c=df_analysis.Days)
ax[0].set_xlim(30000, 120000)
ax[1].scatter(
    df_analysis.Income, df_analysis.Conf,
    s=df_analysis.Population.values / 10000,
    c=days_conf)
ax[2].scatter(
    df_analysis.Income, df_analysis.Growth,
    s=df_analysis.Population.values / 10000,
    c=days_conf)
ax[3].scatter(
    df_analysis.Income, df_analysis.Mortality,
    s=df_analysis.Population.values / 10000,
    c=days_conf)
_ = [axes.grid(True) for axes in ax.flat]
ax[0].set_yscale('log')
ax[1].set_yscale('log')
ax[2].set_yscale('linear')
ax[3].set_yscale('linear')
_ = [axes.set_xlabel('Household Income $') for axes in ax.flat]
ax[0].set_ylabel('COVID metric')
ax[0].set_title('COVID Deaths vs. Income')
ax[1].set_title('COVID Cases vs. Income')
ax[2].set_title('COVID Growth vs. Income')
ax[3].set_title('COVID Mortality vs. Income')
_ = fig.suptitle('US county COVID and Household Income')
_ = [axes.set_ylim(0.001, 100) for axes in ax.flat]
ax[2].set_ylim(0.5, 5)
ax[3].set_ylim(0.0, 0.2)
fig.set_size_inches(w=18, h=6)
fig.tight_layout(pad=3)

fig = plt.figure('US Poverty and COVID')
ax = fig.subplots(ncols=4, sharex=True, sharey=False)
ax[0].scatter(
    df_analysis.Poverty, df_analysis.Death,
    s=df_analysis.Population.values / 10000, c=df_analysis.Days)
ax[0].set_xlim(0, 30)
ax[1].scatter(
    df_analysis.Poverty, df_analysis.Conf,
    s=df_analysis.Population.values / 10000,
    c=days_conf)
ax[2].scatter(
    df_analysis.Poverty, df_analysis.Growth,
    s=df_analysis.Population.values / 10000,
    c=days_conf)
ax[3].scatter(
    df_analysis.Poverty, df_analysis.Mortality,
    s=df_analysis.Population.values / 10000,
    c=days_conf)
_ = [axes.grid(True) for axes in ax.flat]
ax[0].set_yscale('log')
ax[1].set_yscale('log')
ax[2].set_yscale('linear')
ax[3].set_yscale('linear')
_ = [axes.set_xlabel('Poverty %') for axes in ax.flat]
ax[0].set_ylabel('COVID metric')
ax[0].set_title('COVID Deaths vs. Poverty')
ax[1].set_title('COVID Cases vs. Poverty')
ax[2].set_title('COVID Growth vs. Poverty')
ax[3].set_title('COVID Mortality vs. Poverty')
_ = fig.suptitle('US county COVID and Poverty')
_ = [axes.set_ylim(0.001, 100) for axes in ax.flat]
ax[2].set_ylim(0.5, 5)
ax[3].set_ylim(0.0, 0.2)
fig.set_size_inches(w=18, h=6)
fig.tight_layout(pad=3)

Select_State = 'California'
fig = plt.figure('US Income and COVID')
ax = fig.subplots(ncols=4, sharex=True, sharey=True)
ax[0].scatter(
    df_analysis.Income[df_analysis.State == Select_State],
    df_analysis.Death[df_analysis.State == Select_State],
    s=df_analysis[df_analysis.State == Select_State].Population.values / 10000,
    c=df_analysis.Days[df_analysis.State == Select_State])
ax[0].set_xlim(30000, 120000)
ax[0].set_ylim(0.001, 100)
ax[1].scatter(
    df_analysis.Income[df_analysis.State == Select_State],
    df_analysis.Conf[df_analysis.State == Select_State],
    s=df_analysis[df_analysis.State == Select_State].Population.values / 10000,
    c=df_analysis[df_analysis.State == Select_State].Days)
ax[2].scatter(
    df_analysis.Income[df_analysis.State == Select_State],
    df_analysis.Growth[df_analysis.State == Select_State],
    s=df_analysis[df_analysis.State == Select_State].Population.values / 10000,
    c=df_analysis[df_analysis.State == Select_State].Days)
ax[3].scatter(
    df_analysis.Income[df_analysis.State == Select_State],
    df_analysis.Mortality[df_analysis.State == Select_State],
    s=df_analysis[df_analysis.State == Select_State].Population.values / 10000,
    c=df_analysis[df_analysis.State == Select_State].Days)
_ = [axes.grid(True) for axes in ax.flat]
_ = [axes.set_yscale('log') for axes in ax.flat]
_ = [axes.set_xlabel('Income') for axes in ax.flat]
ax[0].set_ylabel('COVID metric')
ax[0].set_title('COVID Deaths vs. Politics')
ax[1].set_title('COVID Cases vs. Politics')
ax[2].set_title('COVID Growth vs. Politics')
ax[3].set_title('COVID Mortality vs. Politics')
_ = fig.suptitle('US county COVID and Political preference for ' + Select_State)
fig.set_size_inches(w=18, h=6)
fig.tight_layout(pad=4)

colorscale = ["#f7fbff","#ebf3fb","#deebf7","#d2e3f3","#c6dbef","#b3d2e9","#9ecae1",
              "#85bcdb","#6baed6","#57a0ce","#4292c6","#3082be","#2171b5","#1361a9",
              "#08519c","#0b4083","#08306b"]
colorscale = [
    'rgb(0, 0, 255)',
    'rgb(0, 63, 255)',
    'rgb(0, 127, 255)',
    'rgb(0, 191, 255)',
    'rgb(0, 255, 255)',
    'rgb(0, 255, 191)',
    'rgb(0, 255, 127)',
    'rgb(0, 255, 63)',
    'rgb(0, 255, 0)',
    'rgb(63, 255, 0)',
    'rgb(127, 255, 0)',
    'rgb(191, 255, 0)',
    'rgb(255, 255, 0)',
    'rgb(255, 191, 0)',
    'rgb(255, 127, 0)',
    'rgb(255, 63, 0)',
    'rgb(255, 0, 0)',
]
endpts = list(np.linspace(-80, 80, len(colorscale) - 1))
fips = df_analysis.index.values
values = df_analysis.Election.values
fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='Trump 2016 [%]',
    legend_title='% for Trump'
)

fig.layout.template = None
fig.show()

colorscale = [
    'rgb(0, 0, 255)',
    'rgb(0, 63, 255)',
    'rgb(0, 127, 255)',
    'rgb(0, 191, 255)',
    'rgb(0, 255, 255)',
    'rgb(0, 255, 191)',
    'rgb(0, 255, 127)',
    'rgb(0, 255, 63)',
    'rgb(0, 255, 0)',
    'rgb(63, 255, 0)',
    'rgb(127, 255, 0)',
    'rgb(191, 255, 0)',
    'rgb(255, 255, 0)',
    'rgb(255, 191, 0)',
    'rgb(255, 127, 0)',
    'rgb(255, 63, 0)',
    'rgb(255, 0, 0)',
]
endpts = list(np.linspace(5, 25, len(colorscale) - 1))
fips = df_analysis.index.values
values = df_analysis.Poverty.values
fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='Poverty in USA',
    legend_title='%'
)

fig.layout.template = None
fig.show()

colorscale = [
    'rgb(0, 0, 255)',
    'rgb(0, 63, 255)',
    'rgb(0, 127, 255)',
    'rgb(0, 191, 255)',
    'rgb(0, 255, 255)',
    'rgb(0, 255, 191)',
    'rgb(0, 255, 127)',
    'rgb(0, 255, 63)',
    'rgb(0, 255, 0)',
    'rgb(63, 255, 0)',
    'rgb(127, 255, 0)',
    'rgb(191, 255, 0)',
    'rgb(255, 255, 0)',
    'rgb(255, 191, 0)',
    'rgb(255, 127, 0)',
    'rgb(255, 63, 0)',
    'rgb(255, 0, 0)',
]
endpts = list(np.linspace(30000, 120000, len(colorscale) - 1))
fips = df_analysis.index.values
values = df_analysis.Income.values
fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='Household Income',
    legend_title='$'
)

fig.layout.template = None
fig.show()

colorscale = ["#f7fbff","#ebf3fb","#deebf7","#d2e3f3","#c6dbef","#b3d2e9","#9ecae1",
              "#85bcdb","#6baed6","#57a0ce","#4292c6","#3082be","#2171b5","#1361a9",
              "#08519c","#0b4083","#08306b"]
colorscale = [
    'rgb(0, 0, 255)',
    'rgb(0, 63, 255)',
    'rgb(0, 127, 255)',
    'rgb(0, 191, 255)',
    'rgb(0, 255, 255)',
    'rgb(0, 255, 191)',
    'rgb(0, 255, 127)',
    'rgb(0, 255, 63)',
    'rgb(0, 255, 0)',
    'rgb(63, 255, 0)',
    'rgb(127, 255, 0)',
    'rgb(191, 255, 0)',
    'rgb(255, 255, 0)',
    'rgb(255, 191, 0)',
    'rgb(255, 127, 0)',
    'rgb(255, 63, 0)',
    'rgb(255, 0, 0)',
]
endpts = list(np.linspace(-2, 5, len(colorscale) - 1))
fips = df_analysis.index.values
values = []
[values.append(np.log10(v)) for v in df_analysis.Death.values]
fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='Death',
    legend_title='COVID Deaths'
)

fig.layout.template = None
fig.show()

colorscale = [
    'rgb(0, 0, 255)',
    'rgb(0, 63, 255)',
    'rgb(0, 127, 255)',
    'rgb(0, 191, 255)',
    'rgb(0, 255, 255)',
    'rgb(0, 255, 191)',
    'rgb(0, 255, 127)',
    'rgb(0, 255, 63)',
    'rgb(0, 255, 0)',
    'rgb(63, 255, 0)',
    'rgb(127, 255, 0)',
    'rgb(191, 255, 0)',
    'rgb(255, 255, 0)',
    'rgb(255, 191, 0)',
    'rgb(255, 127, 0)',
    'rgb(255, 63, 0)',
    'rgb(255, 0, 0)',
]
endpts = list(np.linspace(-1, 6, len(colorscale) - 1))
fips = df_analysis.index.values
values = []
[values.append(np.log10(v)) for v in df_analysis.Conf.values]
fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='Confirmed COVID',
    legend_title='COVID Conf'
)

fig.layout.template = None
fig.show()

colorscale = [
    'rgb(0, 0, 255)',
    'rgb(0, 63, 255)',
    'rgb(0, 127, 255)',
    'rgb(0, 191, 255)',
    'rgb(0, 255, 255)',
    'rgb(0, 255, 191)',
    'rgb(0, 255, 127)',
    'rgb(0, 255, 63)',
    'rgb(0, 255, 0)',
    'rgb(63, 255, 0)',
    'rgb(127, 255, 0)',
    'rgb(191, 255, 0)',
    'rgb(255, 255, 0)',
    'rgb(255, 191, 0)',
    'rgb(255, 127, 0)',
    'rgb(255, 63, 0)',
    'rgb(255, 0, 0)',
]
endpts = list(np.linspace(0.001, 0.1, len(colorscale) - 1))
fips = df_analysis.index.values
values = df_analysis.Mortality.values
fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='Mortality [-]',
    legend_title='[-] Mortality'
)

fig.layout.template = None
fig.show()

colorscale = [
    'rgb(0, 0, 255)',
    'rgb(0, 63, 255)',
    'rgb(0, 127, 255)',
    'rgb(0, 191, 255)',
    'rgb(0, 255, 255)',
    'rgb(0, 255, 191)',
    'rgb(0, 255, 127)',
    'rgb(0, 255, 63)',
    'rgb(0, 255, 0)',
    'rgb(63, 255, 0)',
    'rgb(127, 255, 0)',
    'rgb(191, 255, 0)',
    'rgb(255, 255, 0)',
    'rgb(255, 191, 0)',
    'rgb(255, 127, 0)',
    'rgb(255, 63, 0)',
    'rgb(255, 0, 0)',
]
endpts = list(np.linspace(0.001, 1.5, len(colorscale) - 1))
fips = df_analysis.index.values
values = df_analysis.SecondWave.values
fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='Second Wave',
    legend_title='[-] Second Wave'
)

fig.layout.template = None
fig.show()

colorscale = [
    'rgb(0, 0, 255)',
    'rgb(0, 127, 255)',
    'rgb(0, 255, 255)',
    'rgb(0, 255, 127)',
    'rgb(0, 255, 0)',
    'rgb(127, 255, 0)',
    'rgb(255, 255, 0)',
    'rgb(255, 127, 0)',
    'rgb(255, 0, 0)',
]
endpts = list(np.linspace(1.05, 1.5, len(colorscale) - 1))
fips = df_analysis.index.values
values = df_analysis.Growth.values
fig = ff.create_choropleth(
    fips=fips, values=values,
    binning_endpoints=endpts,
    colorscale=colorscale,
    show_state_data=False,
    show_hover=True, centroid_marker={'opacity': 0},
    asp=2.9, title='Growth [-]',
    legend_title='[-] Growth'
)

fig.layout.template = None
fig.show()

"""# Fitting the data to see correlation"""

x = df_analysis.Election[df_analysis.SecondWave > 0].values
yd_lin = df_analysis.SecondWave[df_analysis.SecondWave > 0].values
yc_lin = df_analysis.Conf.values
yc_lin = df_analysis.Growth.values
yd_log = []
yc_log = []

[yc_log.append(np.log10(yy)) for yy in yc_lin]
[yd_log.append(np.log10(yy)) for yy in yd_lin]

coef = np.polyfit(np.array(x), np.array(yd_lin), 1)
poly1d_fn = np.poly1d(coef) 

plt.plot(x, yd_lin, 'yo')
plt.plot(x, poly1d_fn(x), '-k')

plt.scatter(
    df_analysis.Election,
    df_analysis.SecondWave,
    s=df_analysis.Population / 1e5,
    c=df_analysis.Income,
)
plt.ylim(0.01, 2.5)
plt.yscale('linear')
