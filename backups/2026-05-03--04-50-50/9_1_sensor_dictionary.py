# gpio에 연결
value_dht22 = {
    'DHT22': {
        'Temperature': 23.5,
        'Humidity': 45
    },
    'TempUnit': 'C'    
}

# OnwWire에 여러 개의 센서 연결
value_ds18b20 = {
    'DS18B20_1': {
        'Temperature': 20.5,
        'Humidity': 54
    },
    'DS18B20_2': {
        'Temperature': 25.5,
        'Humidity': 50
    },
    'TempUnit': 'C'    
}

# I2C에 연결
value_bh1750 = {
    'BH1750': {
        'Brightness': 55
    }
}

hum =   value_dht22['DHT22']['Humidity']
temp =  value_ds18b20['DS18B20_2']['Temperature']
unit =  value_ds18b20['TempUnit']
bright = value_bh1750['BH1750']['Brightness']

print(f"DHT22    : 습도 {hum}")
print(f"DS18B20_2: 온도 {temp} {unit}")
print(f"BH1750   : 조도 {bright} lx")
