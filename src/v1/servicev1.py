from statsmodels.tsa.arima_model import ARIMA
import pandas as pd
import pmdarima as pm
from sqlalchemy import create_engine
import json
import os

hours = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00",
         "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00",
         "23:00"]

host = os.environ["HOST"]


class Service:

    def __init__(self):
        # We get a DataFrame with 1000 entries from the DB
        self.engine = create_engine('mysql+pymysql://ivan:ivan@'+host+':3307/forecast')
        # self.df = self.engine.execute("SELECT * FROM forecast LIMIT 1000").fetchall()
        # self.df = pd.DataFrame(data=self.df)

    def predict(self, n_periods):
        try:
            n_periods = int(n_periods)
        except:
            return "{}"

        model_Humidity = pm.auto_arima(self.df[3], start_p=1, start_q=1,
                                       test='adf',       # use adftest to find optimal 'd'
                                       max_p=3, max_q=3,  # maximum p and q
                                       m=1,              # frequency of series
                                       d=None,           # let model determine 'd'
                                       seasonal=False,   # No Seasonality
                                       start_P=0,
                                       D=0,
                                       trace=True,
                                       error_action='ignore',
                                       suppress_warnings=True,
                                       stepwise=True)

        model_Temperature = pm.auto_arima(self.df[2], start_p=1, start_q=1,
                                          test='adf',       # use adftest to find optimal 'd'
                                          max_p=3, max_q=3,  # maximum p and q
                                          m=1,              # frequency of series
                                          d=None,           # let model determine 'd'
                                          seasonal=False,   # No Seasonality
                                          start_P=0,
                                          D=0,
                                          trace=True,
                                          error_action='ignore',
                                          suppress_warnings=True,
                                          stepwise=True)

        fc_Humidity, confint = model_Humidity.predict(
            n_periods=n_periods, return_conf_int=True)

        fc_Temperature, confint = model_Temperature.predict(
            n_periods=n_periods, return_conf_int=True)

        return self.get_json(n_periods, fc_Humidity, fc_Temperature)

    def get_json(self, n_periods, fc_H, fc_T):
        s = '{ "forecast": ['
        for i in range(n_periods):
            s += '{"hour" : "'+str(hours[i % 24])+'","temp": ' + \
                str(fc_T[i])+',"hum": '+str(fc_H[i])+'}'
            if i != n_periods-1:
                s += ","
        s += ']}'
        return json.loads(s)
