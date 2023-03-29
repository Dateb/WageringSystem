class Weather:

    def __init__(self, raw_weather: dict):
        self.temperature = raw_weather["temp"]
        self.feels_like_temperature = raw_weather["feels_like"]
        self.humidity = raw_weather["humidity"]
        self.air_pressure = raw_weather["pressure"]
        self.cloudiness = raw_weather["clouds"]
        self.wind_speed = raw_weather["wind_speed"]
        self.wind_direction = raw_weather["wind_deg"]
