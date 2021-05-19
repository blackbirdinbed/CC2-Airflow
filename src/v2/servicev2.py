import requests
import json
import os

api_key = os.environ["API_KEY"]

class Service:

    def __init__(self):
        # We get the data from Tomorrow.io API
        res = requests.get('https://api.tomorrow.io/v4/timelines?location=37.7749295,-122.4194155&fields=temperature,humidity&timesteps=1h&units=metric&apikey=9BE5Q3qhA5z9aR5Ncza7B6c4boUMXAZR)
        df = res.json()

    def predict(self, n_periods):
        try:
            n_periods = int(n_periods)
        except:
            return "{}"

        return df

    def get_json(self, n_periods, fc_H, fc_T):
        s = '{ "forecast": ['
        for i in range(n_periods):
            s += '{"hour" : "'+str(hours[i % 24])+'","temp": ' + \
                str(fc_T[i])+',"hum": '+str(fc_H[i])+'}'
            if i != n_periods-1:
                s += ","
        s += ']}'
        return json.loads(s)
