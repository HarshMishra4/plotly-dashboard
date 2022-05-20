import pandas as pd
import numpy as np

def melt_df(df:pd.DataFrame, value:str):
    df = df.melt(id_vars='Date').copy()
    df.rename(columns={'value': value}, inplace=True)
    return df

def find_total(df:pd.DataFrame, column:str, max_date):
    total_df = df[df['Date'] == max_date]
    total = total_df[column].sum()
    return total_df, total


def transform(df:pd.DataFrame):
    df = df.groupby(by = 'Country/Region').aggregate(np.sum).T
    df.index.name = 'Date'
    return df.reset_index()

def init():
    # Uncomment for latest data
    # base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
    base_url = 'data/'
    
    # Reference from downloaded file
    confirmed_df = pd.read_csv(base_url + 'time_series_covid19_confirmed_global.csv')
    deaths_df = pd.read_csv(base_url + 'time_series_covid19_deaths_global.csv')
    recovered_df = pd.read_csv(base_url + 'time_series_covid19_recovered_global.csv')


    # Eliminating Columns
    confirmed_df = confirmed_df.drop(columns=['Lat', 'Long', 'Province/State'])
    deaths_df = deaths_df.drop(columns=['Lat', 'Long', 'Province/State'])
    recovered_df = recovered_df.drop(columns=['Lat', 'Long', 'Province/State'])

    # Group_by Country
    confirmed_df = transform(confirmed_df)
    deaths_df = transform(deaths_df)
    recovered_df = transform(recovered_df)

    # Melt
    confirmed_melt_df = melt_df(confirmed_df, 'Confirmed')
    deaths_melt_df = melt_df(deaths_df, 'Deaths')
    recovered_melt_df = melt_df(recovered_df, 'Recovered')

    # Date Format
    confirmed_melt_df['Date'] = pd.to_datetime(confirmed_melt_df['Date'], format="%m/%d/%y")
    deaths_melt_df['Date'] = pd.to_datetime(deaths_melt_df['Date'], format="%m/%d/%y")
    recovered_melt_df['Date'] = pd.to_datetime(recovered_melt_df['Date'], format="%m/%d/%y")

    return confirmed_melt_df, deaths_melt_df, recovered_melt_df