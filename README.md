# Pump it Up: A Cool Title on Tanzania

Despite Tanzania's noteworthy renewable water resources (96.27 km^3 per year), in 2002 it was reported that only 42% of rural households could access "improved" water/water sources and that only 30% of all water systems in the country were opperable. As such, the Government of Tanzaia began a massive sector reform of thier water systems. Unfortunately, due to the decentralization of water management, the weight of improving access to clean water points often falls on local governments with inadequet resources to maintain the extensive systems needed to provide water to far flung rural communities.

With limited resources, it becomes critical to predict the funtionality of wells serving different communities. This allows monies to be spent where they will have the greatest impact. As such, the "Pump It Up" challenge has participants predict wether a given well is "functional", "functional - needs repair", or "non-functional". The data provided for this challenge containes information on the location of the well (latitude/longitude, and multiple features listing which Region/District/Ward/Subvillage), the type, quality, installation date, and management of the well, as well as who funded and installed the well. Unfortunately, again perhaps due to the decentralization of these systems, there exist large swaths of data for which no quantitative data is found. As such, this challenges most important asspects are pattern recognition and value imputation. To this end, I sought to create imputations built on the most granular location information I could find.

## General Overview
In this project, I mine, clean, and process the data provided for the Pump It Up challenge. After the inital cleaning stage, I modele the data using, primarliy, three classification ensemble methods: *Random Forest*, *Gradient Boosting* and *Extreme Gradient Boosting*. For each of these three methods models were built for the full data set and for a reduced data set, with a more parsimonious feature set determined durring the cleaning stage. These naive models were tuned using grid search cross validation and then refit with the optimized parameters. The tuned models were then used to create predictions on the provided testing data set. Finally, the generated predictions were submitted to the [challange page]() for scoring.

### Understanding the Geographical Divisions of Tanzania
To understand the location feature levels in the data, it is helpful to have a gneral understanding of the geographical divisions of Tanzania itself.
Tanzania is divided into 31 different *regions*, which themselves are then subdivided into *districts*. Districts are further subdivided into *divisions* and then into *wards*. Wards then have two types: *urban wards* which can be split into streets, and *rural wards* which can be split into villages. [<sup>2</sup>](2) This information is captured in the challenge data under the labels `region`, `lga`, `ward`, and `subvillage`, with respect to increasing granularity. My analysis focuses on the first three of these, as I found that the `subvillage` feature had more than 19,000 unique levels.

**Regions**
<img align="left" style="border:10px solid white" width = 300 src="Images/Tanzania_Admin_Regions.png" alt = "A map showing the locations in which ceratin Dravidian language family members are spoken."> As of 2016, Tanzania has been divided into 31 different regions. As the water system management is highly decentralized, accurate location data is key to predicting the functionality well and to understanding the area around the well. To this end, I utilized publically avaliable Tanzania census data from 2012, which is included here in this repo, to correctly adjust any mislabeled divisions of the regions, districts, and wards such that they were an accurate representation of the divisions of Tanzania at the time of the most recent data collection (2013).

### The Data
The data used in this analysis was taken from the Taarifa waterpoints dashboard, which provides an aggregation of data from the Tanzania Ministry of Water. It can be found on the [DrivenData competition page](https://www.drivendata.org/competitions/7/pump-it-up-data-mining-the-water-table/page/23/), although it can only be downloaded by competitors/DrivenData account holders. It's entirely free to sign up, if you'd like access to the data. An explanation of the various features, an example record, and a small explanation of the target feature can be found [here](https://www.drivendata.org/competitions/7/pump-it-up-data-mining-the-water-table/page/25/). I've also provided my own extensive notes on the data in the "Cleaning Analysis and Notes" notebook, which can be found here in the repo.

### Exploratory analysis
The full notes for the exploratory analysis conducted for this project can be found in the [FILE NAME] file.

The majority of the data was found to be qualitative, and of these only a handful were found to have missing values. These are more fully discussed in the **Data Imputation** section. On the majority of cases, the missing values were given their own level and encoded along with the other levels of the categorical variables before modeling. In some cases where the class imblance was notably high, and very few missing values existed, these values were filled with the most common level for the ward in which the observation was found.

Although there were far fewer numerical features, these two were found to have notable amounts of missing features. Zero was used as the missing flag in this data for the numerical features. As such, I decided to fill all numerical missing values using, in the majority case, mean imputation. These means were calculated on the most granular location information possible, as the majority of the numerical feature distributions were highly dependant on location.

### Data Imputation
#### Quantitative Features
The first natural step in imputing the numerical features was to correct and update the location information in the challenge data set, such that it reflected the divisions of Tanzania as they stood at the time of the 2012 census. To this end I created a dictionary of all reagions, each region itself being a dictionary of all districts, and each district a dictionary containing information on the wards. I also stored in this dictionary information on the total population for each region, district, and ward, such that the population information in the challenge data set would be updated to reflect the numbers taken in the 2012 Tanzaia census.

After updating the location information, I used the average population values, calculated from the above described dictionary, to estiamte the average population across the district, and imputed this for all observations where the population had been marked as zero. The updated location information was also used when computing the mean to fill the `amount_tsh` and `construction_year` features.

When no information was avaliable across an entire region, three seperate methods were used to imput the three numerical features (`population`, `amount_tsh`, `construction_year`) filled using imputation.
1. Method for `population`: Divide the collected population value for the ward by the number of observations in the ward, to determine an average value. Imput this average.
2. Method for `amount_tsh`: Imput the data set mean, rather than a more granular mean.
3. Method for `construction_year`: Fit the data with a `loggamma` distribution. Generate imputation values randomly from this distribution, rescriting the cieling and floor of these estimates to the minimum and maximum of the training data.

#### Latitude and Longitude
Missing longitude values were marked with 0, while missing latitudes were marked with the value -2.000000e-08. These missing values were found to be linked (anywhere the longitude was missing, so was the latitude). Once the regions were updated, these missing values were filled using the average value for the region in which thee observations were recorded.

#### Qualitative Features
The greatest number of missing values was in the `scheme_name` feature, with more than 28,000 missings. This feature was dropped from the modeling data, due to the inredibly high proportion of missings. Other categorical values with missings values were,
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

### Modeling
In order to model this data I selected three different ensemble methods: *random forest*, *gradient boost*, and *extreme gradient boosting*. For each of these I created two models: one using the full feature set, not including any of those variables dropped to their missing values of high number of levels, and one using a more parsimonious feature set, selected based on the full cleaning analysis. These models were then each tuned to discover their optimal parameters, and refit using them. The final, tunened models were then used to generate predicitons on the provided test set.

#### Random Forest
The two random forest models yeilded average accuracies of 81.17% and 81.14% for the full model and the parsimonious model, respectively, once fully tuned.

<p float="center">
  <img src="Images/RF_Full_VarImp.png" alt="GBM Feature Importance" width=425 />
  <img src="Images/RF_Pars_VarImp.png" alt="XGBoost Feature Importance" width="425" />
</p>


#### Gradient Boosting


#### Extreme Gradient Boosting


## Requirements
The requirements to run any portion of this project on your local machine are found in the `requirements.txt` file.








[1]: https://en.wikipedia.org/wiki/Water_supply_and_sanitation_in_Tanzania#cite_note-8 "Water supply and sanitation in Tanzania - Wikipedia"
[2]: https://en.wikipedia.org/wiki/Regions_of_Tanzania "Regions of Tanzania - Wikipedia"
