import requests
import json
class Service:

    def __init__(self):
        # We get the data from Tomorrow.io API
        res = requests.get('https://api.tomorrow.io/v4/timelines?location=37.7749295,-122.4194155&fields=temperature,humidity&timesteps=1h&units=metric&apikey=9BE5Q3qhA5z9aR5Ncza7B6c4boUMXAZR')
        self.df = res.json()

    def predict(self, n_periods):
        try:
            n_periods = int(n_periods)
        except:
            return "{}"

        return self.get_json(n_periods)

    def get_json(self, n_periods):
        s = '{ "forecast": ['
        for i in range(n_periods):
            s += '{"hour" : "'+ self.df['data']['timelines'][0]['intervals'][i]['startTime'] + \
                '","temp": ' + self.df['data']['timelines'][0]['intervals'][i]['temperature'] + \
                ',"hum": '+ self.df['data']['timelines'][0]['intervals'][i]['humidity'] +'}'
            if i != n_periods-1:
                s += ","
        s += ']}'
        return json.loads(s)
