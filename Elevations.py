import os
import pandas as pd
import numpy as np
import requests
from Keys import access_token

#~~~~~~~~~~#
#Defining Functions

#EASY READ AND WRITE FUNCTIONS
def read_train():
    X_train = pd.read_csv("Data/Raw/Train.csv")
    return(X_train)

def write(X_train, file = "Train.csv"):
    X_train.to_csv("Data/Processed/{}".format(file))

##Adding elevation, to supplement "gps_height"
def get_elevation_single(lat, long, access_token = access_token):
    #This function will query the Jawg API
    #using a given latitude and longitude
    #You need an access token for the Jawg API, but they can be aquired for free through their website
    query = ('https://api.jawg.io/elevations?locations={},{}&access-token={}'.format(lat, long, access_token))
    r = requests.get(query).json()

    #extracting elevation from the json object
    elevation = pd.io.json.json_normalize(r)['elevation'].values[0]
    return(elevation)

def get_elevation_series(lat_series, long_series, access_token = access_token):
    #This will use the get_elevation_single function
    #And apply it to a series

    elevations = []
    for i in range(len(lat_series)):
        try:
            elevations.append(get_elevation_single(lat_series[i], long_series[i], access_token))
        except:
            try:
                elevations.append(get_elevation_single(lat_series[i], long_series[i], access_token))
            except:
                elevations.append(-1)

        if i % 1000 == 0:
            print(i)
    return(elevations)

#~~~~~~~#
#Main

if __name__ == "__main__":

#Filling Training set values
    access_token = access_token
    X_train = read_train()
    X_train = fill_lat_long(X_train, 0, -2.000000e-08)


    #This step takes SO LONG. I need to run it somewhere else, although I'll leave it here for reference
    #Consider doing it piece-wise?
    #X_train['well_elevations'] = get_elevation_series(X_train['latitude'], X_train['longitude'], access_token)
    write(X_train)

#Filling Testing set values
