# Pump it Up: A Cool Title on Tanzania

Despite Tanzania's noteworthy renewable water resources (96.27 km^3 per year), in 2002 it was reported that only 42% of rural households could access "improved" water/water sources and that only 30% of all water systems in the country were opperable. As such, the Government of Tanzaia began a massive sector reform of thier water systems. Unfortunately, due to the decentralization of water management, the weight of improving access to clean water points often falls on local governments with inadequet resources to maintain the extensive systems needed to provide water to far flung rural communities.

With limited resources, it becomes critical to predict the funtionality of wells serving different communities. This allows monies to be spent where they will have the greatest impact. As such, the "Pump It Up" challenge has participants predict wether a given well is "functional", "functional - needs repair", or "non-functional". The data provided for this challenge containes information on the location of the well (latitude/longitude, and multiple features listing which Region/District/Ward/Subvillage), the type, quality, installation date, and management of the well, as well as who funded and installed the well. Unfortunately, again perhaps due to the decentralization of these systems, there exist large swaths of data for which no quantitative data is found. As such, this challenges most important asspects are pattern recognition and value imputation. To this end, I sought to create imputations built on the most granular location information I could find.

## Understanding the Geographical Divisions of Tanzania
Tanzania is divided into 31 different *regions*, which themselves are then subdivided into *districts*. Districts are further subdivided into *divisions* and then into *wards*. Wards then have two types: *urban wards* which can be split into streets, and *rural wards* which can be split into villages. [<sup>2</sup>](2) This information is captured in the challenge data under the labels `region`, `lga`, `ward`, and `subvillage`, with respect to increasing granularity. My analysis focuses on the first three of these, as I found that the `subvillage` feature had more than 19,000 unique levels.

**Regions**
<img align="left" style="border:10px solid white" width = 300 src="Images/Tanzania_Admin_Regions.png" alt = "A map showing the locations in which ceratin Dravidian language family members are spoken."> As of 2016, Tanzania has been divided into 31 different regions. The Songwe Region is the most recently created of these. It was split from the western portion of the Mbeya region, seen here in the left-hand corner of Tanzania, in 2016. The challenge data only covers up to 2013, so, as with the map to the left, it is not included in this analysis.

The next most recently created regions are the Geita, Katavi, Njombe, and Simiyu Regions, all originating in 2012. Through my inspection of the location data avliable in the challenge data set, I discovered that these regions are also not included, although all data was recorded after their creation. As the water system management is highly decentralized, accurate location data is key to predicting the functionality well and to understanding the area around the well. To this end, I utilized publically avaliable Tanzania census data from 2012, which is included here in this repo, to correctly adjust the regions, districts, and ward such that they would be classified under the existing at the point of data collection (2013).

## General Overview

### The Data
The data used in this analysis was taken from the Taarifa waterpoints dashboard, which provides an aggregation of data from the Tanzania Ministry of Water. It can be found on the [DrivenData competition page](https://www.drivendata.org/competitions/7/pump-it-up-data-mining-the-water-table/page/23/), although it can only be downloaded by competitors/DrivenData account holders. It's entirely free to sign up, if you'd like access to the data. An explanation of the various features, an example record, and a small explanation of the target feature can be found [here](https://www.drivendata.org/competitions/7/pump-it-up-data-mining-the-water-table/page/25/). I've also provided my own extensive notes on the data in the "Cleaning Analysis and Notes" notebook, which can be found here in the repo.

### Exploratory analysis
All notes for the exploratory analysis conducted for this project can be found in the [FILE NAME] file.

Many of the featues in the data set were found to have some missing vaules. In the case of the quantiative features, the majority were found to have some missing values, frequently many. Zero was used as the missing flag in this data for the numerical features, somewhat unfortunately, as I strongly believe that there also exist true zero values in the data, meaning there was no way to distinguish between flags and actual zeros. As such, I decided to treat any zero value as a missing flag, and to fill all of them using, for the majority of the missing values, mean imputation. These means were calculated of the most granular location information possible the majority of the numerical feature distributions were highly dependant on location.

The majority of the data was qualitative, and of these only a handful were found to have missing values. These are more fully discusseed in the **Data Imputation** section.

### Data Imputation
#### Quantitative Features

The first natural step in imputing the numerical features was to correct and update the location information in the challenge data set, as described above. To this end I created a dictionary of all reagions, each region then itself being a dictionary of all districts, and each district a dictionary containing information on the wards. I also stored in this dictionary information on the total population for each region, district, and ward, such that the population information in the challenge data set would be updated to reflect the numbers taken in the 2012 Tanzaia census.

After updating the location information, I used the average population values, calculated from the above described dictionary, to estiamte the average population on the most granular level possible, and imputed this for all observations where the population had been marked as zero. The updated location information was also used when computing the mean to fill the `amount_tsh` and `construction_year` features.

When no information was avaliable across an entire region, three seperate methods were used to imput the three numerical features (`population`, `amount_tsh`, `construction_year`) filled using imputation. The first, used for `population`, was based on the above described dictionary object. Here the collected population value for the ward was divided by the number of observations in the ward, to determine an average value, which was then imputed. The second of these, used for `amount_tsh`, was to simply imput the data set mean, rather than a more granular mean. Finally, for `construction_year`, it was found that the data could be relatively well fit with a `loggamma` distribution. As such, random values from this distribution were generated and imputed into these missing values, resricting any generated values to the maximum and minimum values allready seen in the data.

#### Latitude and Longitude
The next features which I saw need imputation were the latitude and longitude values which were flagged as missing. Missing longitude values were marked with 0, while missing latitudes were marked with the value -2.000000e-08. These were entirely linked (anywhere the longitude was missing, so was the latitude). These were filled, once the regions were updated, using the average value for the region in which they were recorded.

#### Qualitative Features
The majority of the features in the date set are categorical, and of these only a handful experienced any missing values. The greatest number of missings was in the `scheme_name` feature, with more than 28,000 missing values. This was dropped from the modeling data, due to the inredibly high proportion of missings. Other categorical values with missings values were,
+ funder
+ installer
+ subvillage
+ public_meeting
+ scheme_management
+ permit

Of these, only `permit` and `public_meeting` were kept, and the missing values were simply encoded as unknowns.

Both funder and installer were found to have both notably high numbers of unique levels, as well as many, many inconsistencies in spelling and language. For example, it appears that a few wells were funded by the Swedish government. These different wells are listed as being funded by:
+ Sweden
+ Swedish
+ Sweeden
+ Swidish

Due to the high rates of irregularity in these features, they were dropped from the modeling data set. `scheme_management` was also dropped, as it was found to contain information highly simmilar to that captured by `management`, a feature with no missing values.









[1]: https://en.wikipedia.org/wiki/Water_supply_and_sanitation_in_Tanzania#cite_note-8 "Water supply and sanitation in Tanzania - Wikipedia"
[2]: https://en.wikipedia.org/wiki/Regions_of_Tanzania "Regions of Tanzania - Wikipedia"
