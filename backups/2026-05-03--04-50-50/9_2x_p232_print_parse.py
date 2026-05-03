from parse import Parse
data = {'DHT22': {'Temperature': 25.6, 'Humidity': 45}, 'TempUnit': 'C'}
p = Parse(data)
print(p.name) # 'DHT222'
print(p.names) # ['DHT22']
print(p.key) # 'Humidity'
print(p.keys) # ['Humidity','Temperatute']
print(p.value) # 45
print(p.values) # [45,25,6]
print(p.temp_unit) # 'C'