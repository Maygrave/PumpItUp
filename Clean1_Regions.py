import os
import pandas as pd
import numpy as np
import requests
from Keys import access_token
import Settings as Sts

#~~~~~~~~~~#
#Defining Functions

#EASY READ AND WRITE FUNCTIONS
def read_train():
    X_train = pd.read_csv("Data/Raw/Train.csv")
    return(X_train)

def write(X_train, file = "Train1.csv"):
    X_train.to_csv("Data/Processed/{}".format(file))

##Regions
def update_regions(data):
    #Add simiyu, geita, katavi, njombe regions
    ##Simiyu
    simiyu_index = data[(data['region'] == 'Shinyanga') & ((data['lga'].isin(["Maswa","Meatu","Bariadi"]))].index
    data.loc[simiyu_index, 'region']  = "Simiyu"
    ##Geita
    geita_index = data[((data['region'].isin(["Shinyanga", "Mwanza", 'Kagera']))) & ((data['lga'].isin(["Bukombe", "Chato", "Geita"]))].index
    data.loc[geita_index, 'region'] = 'Geita'
    ##Katavi
    katavi_index = data[(data['region'] == "Rukwa") & (data['lga'] == "Mpanda")].index
    data.loc[katavi_index, 'region'] = 'Katavi'
    data.loc[katavi_index, 'lga'] = 'Mpanda Rural'
    ##Njombe
    njombe_index = data[(data['region'] == 'Iringa') & ((data['lga'].isin(["Ludewa", "Njombe", "Makete"]))].index
    data.loc[njombe_index, 'region'] = "Njombe"

    #Fixing Mislabeled Regions/LGAS/Wards
    ##Creating the "Nyang'hwale" LGA in the Geita region
    nyang_index = data[(data['region'] == 'Geita') & ((data['ward'].isin(["Nyang'hwale", 'Busolwa', 'Bukwimba', 'Mwingiro','Nyugwa','Kakora', 'Kharumwa','Shabaka','Kafita']))].index
    data.loc[nyang_index, 'lga'] = "Nyang'hwale"

    ##Creating Chemba District in Kidodoma
    chemba_index = data[(data['region'] == 'Dodoma') & (data['lga'] == 'Kondoa') & (data['ward'].isin(['Farkwa','Kwamtoro', 'Dalai', 'Chandama', 'Lalta', 'Chemba', 'Sanzawa', 'Jangalo','Goima', 'Mrijo', 'Mondo', 'Mpendo','Ovada','Makorongo']))].index
    data.loc[chemba_index, 'lga'] = 'Chemba'

    ##Creating the Gairo district in Morogoro
    gairo_index = data[(data['region'] == 'Morogoro') & (data['lga'] == 'Kilosa') & (data['ward'].isin(['Chakwale', 'Rubeho', 'Kibedya', 'Iyogwe',  'Gairo', ]))].index
    data.loc[gairo_index, 'lga'] = "Gairo"

    #Changin wards in Linidi dicstrict from rural to urban where necessary
    lindi_index = data[(data['region'] == "Lindi") & (data['lga'] == "Lindi Rural") & (data['ward'].isin(['Tandangongoro', 'Chikonji', "Ng'apa", 'Mngoyo', 'Mbanja']))].index
    data.loc[lindi_index, 'lga'] = "Lindi Urban"

    #Moving from Songea Rural to Songea Urban (Ruvuma district)
    songea_index = data[(data['region'] == 'Ruvuma') & (data['lga'] == 'Songea Rural') & (data['ward'].isin(['Lilambo', 'Tanga']))].index
    data.loc[songea_index, 'lga'] = 'Songea Urban'

    #Creating Nyasa lga in Ruvuma district
    nyasa_index = data[(data['region'] == 'Ruvuma') & (data['lga'] == 'Mbinga') & (data['ward'].isin(['Lipingo', 'Liuli', 'Tingi', 'Chiwanda', 'Kingerikiti', 'Lituhi', 'Mbaha', 'Kihagara', 'Kilosa', 'Mtipwili', 'Mbamba bay']))].index
    data.loc[nyasa_index, 'lga'] = 'Nyasa'

    #Moving Katumba to Keyla from Rungwe
    katumba_index = data[(data['region'] == 'Mbeya') & (data['ward'] == 'Katumba')].index
    data.loc[katumba_index, 'lga'] = 'Keyla'

    #Creating the Mkalama district (split from Iramba in Singida in 2010) and the Ikungi (Split from Singida Rural in 2010)
    mkalama_index = data[(data['region'] == "Singida") & (data['lga'] == 'Iramba') & (data['ward'].isin(['Nduguti', 'Msingi', 'Nkinto', 'Mpambala', 'Kinyagiri', 'Mwanga', 'Gumanga', 'Ilunda', 'Ibaga', 'Iguguno']))].index
    data.loc[mkalama_index, 'lga'] = 'Mkalama'
    ikungi_index =  data[(data['region'] == "Singida") & (data['lga'] == 'Singida Rural') & (data['ward'].isin(['Ihanja', 'Irisya', 'Mgungira', 'Misughaa', 'Minyughe', 'Puma', 'Ntuntu', 'Ikungu', 'Siuyu', "Mang'onyi", "Dung'unyi", 'Sepuko', 'Mwaru', "Munga'a", 'Issuwa']))].index
    data.loc[ikungi_index, 'lga'] = 'Ikungi'

    #Creating Kaliua district in tabora region
    kaliua_index = data[(data['region'] == 'Tabora') & (data['lga'] = 'Urambo') & (data['ward'].isin(['Ugunga', 'Igalala', 'Kanindo', 'Ushokola', 'Mwongozo', 'Igombe Mkulu', 'Kaliua', 'Ukumbisiganga', 'Kazaroho', 'Uyowa', 'Ichemba', 'Milambo', 'Usinge', 'Kashishi']))].index
    data.loc[kaliua_index, 'lga'] = 'Kaliua'

    #Creating the Kalambo district in the Rukwa region
    kalambo_index = data[(data['region'] == 'Rukwa') & (data['lga'] == 'Sumbawanga Rural') & (data['ward'].isin(['Mkowe', 'Mambwekenya', 'Katazi', 'Legezamwendo', 'Mwimbi', 'Msanzi', 'Matai', 'Sopa', 'Mwazye', 'Kasanga', 'Mambwenkoswe']))].index
    data.loc[kalambo_index, 'lga'] = 'Kalambo'

    #Creating the additional discticts in the Kigoma region
    kakonko_index = data[(data['region']=='Kigoma') & (data['lga'] == 'Kibondo') & (data['ward'].isin(['Muhange', 'Kasanda', 'Mugunzu', 'Kakonko', 'Rugenge', 'Gwanumpu', 'Nyabibuye', 'Nyamtukuza', 'Kasuga']))].index
    data.loc[kakonko_index, 'lga'] = 'Kakonko'
    kusulu_index = data[(data['region'] == 'Kigoma') & (adta['lga'] == 'Kasulu') & (data['ward'].isin(['Msambara', 'Ruhita', 'Murufiti', 'Muhunga', 'Kigondo']))].index
    dataa.loc[kusulu_index, 'lga'] = 'Kusulu Town'
    buhigwe_index = data[(data['region'] == 'Kigoma') & (adta['lga'] == 'Kasulu') & (data['ward'].isin(['Munyegera', 'Buhigwe', 'Rusaba', 'Muhinda', 'Munzenze', 'Janda', 'Kilelema', 'Muyama']))].index
    data.loc[buhigwe_index, 'lga'] = 'Buhigwe'
    uvinza_index = data[(data['region'] == 'Kigoma') & (adta['lga'] == 'Kigoma Rural') & (data['ward'].isin(['Sunuka', 'Mtego wa Noti', 'Mganza', 'Kandaga', 'Uvinza', 'Ilagala', 'Nguruka', 'Simbo']))].index
    data.loc[uvinza_index, 'lga'] = 'Uvinza'

    #Creating Kahama Town in Shinyanga
    kahama_index = data[(data['region'] == 'Shinyanga') & (data['lga'] == 'Kahama') & (data['ward'].isin(['Isagehe', 'Mhongolo', 'Kinaga', 'Kahama Urban', 'Zongomera', 'Kilago', 'Malunga', 'Ngongwa', 'Nyandekwa', 'Mwendakulima']))].index
    data.loc[kahama_index, 'lga'] = 'Kahama Town'

    #Creating Kyerwa in Kagera
    kyewra_index = adta[(data['region'] == 'Kagera') & (data['lga'] == 'Karagwe') & (data['ward'].isin(['Kyerwa', 'Kaisho', 'Isingiro', 'Kamuli', 'Nkwenda', 'Murongo', 'Bugomora', 'Kibingo', 'Mabira', 'Kimuli']))].index
    data.loc[kyewra_index, 'lga'] = 'Kyerwa'

    #Moving Mwzana obs to simiyu
    busega_index = data[(data['region'] == 'Mwanza') & (data['lga'] == 'Magu') & (data['ward'].isin(['Kabita', 'Badugu', 'Mwananyili', 'Mkula', 'Nyaluhande', 'Kalemela', 'Malili', 'Shigala', 'Kiloleli', 'Ngasamo', 'Igalukilo']))].index
    data.loc[busega_index, 'lga'] = 'Busega'
    data.loc[busega_index, 'region'] = 'Simmiyu'

    #Moving obs to Nyamagana in Mwzana
    nyama_index = data[(data['region'] == "Mwanza") & (data['ward'].isin(['Mkolani', 'Butimba', 'Buhongwa']))].index
    data.loc[nyama_index, 'lga'] = 'Nyamagana'

    #Updating values from Tarime to Rorya
    rorya_index = data[(data['region'] == 'Mara') & (data['lga'] == 'Tarime') & (data['ward'].isin(['Goribe', 'Bukura','Roche','Tai']))].index
    data.loc[rorya_index, 'lga'] = 'Rorya'

    #Creating Musoma Urban and Butaima In Mara
    #musoma_index = data[(data['region'] == 'Mara') & (data['lga'] == 'Musoma Rural') & (data['ward'].isin([]))].index
    #data.loc[musoma_index, 'lga'] = 'Musoma Urban'
    butiama_index = data[(data['region'] == 'Mara') & (data['lga'] == 'Musoma Rural') & (data['ward'].isin(['Buswahili', 'Nyamimange', 'Etaro', 'Masaba', 'Buhemba', 'Kyanyari', 'Nyankanga', 'Nyakatende', 'Muriaza', 'Butiama', 'Buruma', 'Bukabwa', 'Bwiregi', 'Kukirango', 'Butuguri', 'Buswahili']))].index
    data.loc[butiama_index, 'lga'] = 'Butiama'

    #Creating the LGAs in njombe
    Njombe_urban_index = data[(data['region'] == 'Njombe') & (data['lga'] == 'Njombe') & (data['ward'].isin(['Idamba', 'Ikondo', 'Lupembe', 'Mtwango', 'Kidegembye', 'Igongolo']))].index
    data.loc[Njombe_urban_index, 'lga'] = 'Njombe Urban'
    wang_index = data[(data['region'] == 'Njombe') & (data['lga'] == 'Njombe') & (data['ward'].isin(['Ilembula', 'Imalinyi', 'Mdandu', 'Usuka', 'Saja', "Wanging'ombe", 'Igosi', 'Wangama', 'Luduga']))].index
    data.loc[wang_index, 'lga'] = "Wanging'ombe"
    maka_index = data[(data['region'] == 'Njombe') & (data['lga'] == 'Njombe') & (data['ward'].isin(['Mahongole', 'Makambako']))].index
    data.loc[maka_index, 'lga'] = 'Makambako'
    Njombe_rural_index = data[(data['region'] == 'Njombe') & (data['lga'] == 'Njombe') & (data['ward'].isin(['Usuka', 'Matola', 'Ikuka','Uwemba', 'Kifanya', 'Luponde', 'Njombe Urban', 'Iwungilo', 'Yakobi']))].index
    data.loc[Njombe_rural_index, 'lga'] = 'Njombe Rural'

    #Adding LGAs to Katavi
    mp_urb_index = data[(data['region'] == 'Katavi') & (data['lga'] == 'Mpanda Rural') & (data['ward'].isin(['Mishamo', 'Mpanda Ndogo', 'Mwese', 'Karema', 'Ikola', 'Katuma', 'Kabungu']))].index
    data.loc[mp_urb_index, 'lga'] = 'Mpanda Urban'
    mlele_index = data[(data['region'] == 'Katavi') & (data['lga'] == 'Mpanda Rural') & (data['ward'].isin(['Ugala', 'Mtapenda', 'Kibaoni', 'Mbede', 'Utende', 'Ilela', 'Mamba', 'Usevya', 'Kasokola', 'Nsimbo', 'Inyonga', 'Sitalike', 'Magamba', 'Machimboni', 'Ilunde',  'Urwira']))].index
    data.loc[mlele_index, 'lga'] = 'Mlele'

    #Adding Itilima in Simiyu
    itilima_index = data[(data['region'] == 'Simiyu') & (data['lga'] == 'Bariadi') & (data['ward'].isin(['Lagangabilili', 'Mbita', 'Mwaswale', 'Lugulu', "Kinang'weli", 'Sagata', 'Chinamili', 'Nkoma', 'Bumera', 'Mwamapalala', 'Mhunze', 'Zagayu']))].index
    data.loc[itilima_index, 'lga'] = 'Itilima'

    #Adding Mbongwe in geita
    mbongwe_index = data[(data['region'] == 'Geita') & (data['lga'] == 'Bukombe') & (data['ward'].isin(['Mbogwe', 'Ushirika', 'Masumbwe', 'Nyasato', 'Lugunga', 'Ilolangulu', 'Ikunguigazi', 'Iponya']))].index
    data.loc[mbongwe_index, 'lga'] = 'Mbongwe'


#~~~~~~~~~#

if __name__ == "__main__":
