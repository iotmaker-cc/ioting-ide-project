
# file:parse.py
class Parse:
    def __init__(self,data: dict):
        
        self.name = ''
        self.names = []
        
        self.temp_unit = ''
        
        self.key = ''
        self.keys = []
        
        self.value = 0
        self.values = []
        
        self.ow_id = ''
        self.ow_ids = []
        self.ow_key = 0
        self.ow_keys = []    
        self.ow_value = 0
        self.ow_values = []     
        
        self.data = data
        if not isinstance(self.data,dict):
            return
        
        self._arrange_data()              
            
    def _arrange_data(self):
        
        try:
            
            names  = list(self.data.keys())
                
            if 'TempUnit' in names:
                self.temp_unit = self.data['TempUnit']
                names.remove('TempUnit')
                
            names.sort()
            self.name = names[0]
            self.names = names
            
            keys = list(self.data[names[0]].keys())
            keys.sort()
            values = []
            
            ow = False
            for k in keys:
                if k == 'Id':
                    ow = True                
                values.append(self.data[names[0]][k])
                
            self.key = keys[0]
            self.keys = keys
            self.value = values[0]
            self.values = values
                
            if ow:
                ow_keys = []
                ow_values = []
                ow_ids = []
                for name in names:
                    keys = list(self.data[name].keys())
                    keys.sort()                    
                    for k in keys:
                        if k == 'Id':
                            ow_ids.append(self.data[name][k])
                        else:
                            ow_keys.append(k)
                            ow_values.append(self.data[name][k])
                        
                self.ow_key = ow_keys[0]
                self.ow_keys = ow_keys
                self.ow_value = ow_values[0]
                self.ow_values = ow_values
                self.ow_id = ow_ids[0]
                self.ow_ids = ow_ids
            else:
                self.ow_key = ''
                self.ow_keys = ['']
                self.ow_value = 0
                self.ow_values = [0]
                self.ow_id = ''
                self.ow_ids = ['']
                
        except ValueError:
            pass
        except IndexError:
            pass
        
if __name__ == '__main__':
    
    data = [None] * 5
    
    data[0] = {'BH1750': {'LightIntensity': 450.8}}    
    data[1] = {'DHT22': {'Temperature': 45.2, 'Humidity': 53}}
    data[2] = {'DHT22': {'Temperature': 45.2, 'Humidity': 53},'TempUnit': 'C'}
    data[3] = {'DS18B20_1': {'Id': '12345678','Temperature': 45.1}, 'TempUnit': 'C'}
    data[4] = {'DS18B20_1': {'Id': '12345678','Temperature': 45.1}, 'DS18B20_2': {'Id': '22345678','Temperature': 45.2},'TempUnit': 'C'}
    
    for i,d in enumerate(data):
        p = Parse(d)
        print()
        print(d)
        print(f'names: {p.names}, keys: {p.keys}, values: {p.values}, temp_unit: {p.temp_unit}')
#         if i == 3 or i == 4:
#             print(f'names: {p.names}, ow_ids: {p.ow_ids},ow_keys: {p.ow_keys}, ow_values: {p.ow_values}, temp_unit: {p.temp_unit}')
        print(f'names: {p.names}, ow_id: {p.ow_ids[0]},ow_ids: {p.ow_ids},ow_keys: {p.ow_keys}, ow_values: {p.ow_values}, temp_unit: {p.temp_unit}')
            
        
  
    