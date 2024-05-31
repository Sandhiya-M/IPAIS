import os
import requests
import math
import openpyxl
import geocoder
crop_kc_values = openpyxl.load_workbook("CROP_NEEDS.xlsx") 

print(crop_kc_values.sheetnames)
def get_weather(api_key, latitude, longitude):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "units": "metric"  
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to retrieve weather data.")
        return None

def PET_helper(temp, wind_speed, humidity):
    gamma = 0.665 * 10 ** -3
    atm_pressure = 101.3  
    psychometric_constant = gamma * atm_pressure / 0.622    
    wind_speed_kmh = wind_speed * 3.6
    delta = 4098 * (0.6108 * math.exp((17.27 * temp) / (temp + 237.3))) / ((temp + 237.3) ** 2)
    Rn = 10  
    G = 0.1  
    
    # Magnus formula
    es = 0.6108 * math.exp((17.27 * temp) / (temp + 237.3))  # Saturation vapor pressure (kPa)
    ea = (humidity / 100) * es  # Actual vapor pressure (kPa)

    # Penman-Monteith equation 
    pet = (0.408 * delta * (Rn - G) + gamma * (900 / (temp + 273)) * wind_speed_kmh * (es - ea)) / (delta + gamma * (1 + 0.34 * wind_speed_kmh))
    return pet


def get_PET_PMA():
    api_key = open('api key_Girish.txt','r').read()
    location = geocoder.ip('me')
    latitude, longitude = location.latlng

    weather_data = get_weather(api_key, latitude, longitude)
    if weather_data:
        city = weather_data['name'] 
        state = weather_data['sys']['country'] 
        temperature = weather_data['main']['temp']  
        humidity = weather_data['main']['humidity'] 

        print(f"Weather in {city}, {state}:")
        print(f"Temperature: {temperature}°C")
        print(f"Humidity: {humidity}%")

        elevation = 2  

        pet = PET_helper(temperature, weather_data['wind']['speed'], humidity)
        print(f'Potential Evapotranspiration (PET) using Penman-Monteith equation: {pet} mm/day')
        return pet

def get_kc_value_from_excel(stage='mid',crop='Cabbage'):
    sheet = crop_kc_values.worksheets[3] 
    values=[]
    for i,row in enumerate(sheet):
        if(i==0 or i==1):
            continue
        crop_name=row[0].value
        if(crop_name==crop):
            if(stage=='mid'):
              values.append(row[3].value)
    print(values)
    return values


if __name__=='__main__':
    pet=get_PET_PMA()
    kc=get_kc_value_from_excel()[0]
    Etc=pet*kc
    print("Required water need for the crop (mm/day)"+str(Etc))

