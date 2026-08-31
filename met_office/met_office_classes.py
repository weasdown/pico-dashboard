class Datapoint:
    def __init__(self, time: str, screenTemperature: float, maxScreenAirTemp: float, minScreenAirTemp: float, screenDewPointTemperature: float,
                feelsLikeTemperature: float, windSpeed10m: float, windDirectionFrom10m: int, windGustSpeed10m: float, max10mWindGust: float,
                visibility: int, screenRelativeHumidity: float, mslp: int, uvIndex: int, significantWeatherCode: int, precipitationRate: float,
                totalPrecipAmount: float, totalSnowAmount: float, probOfPrecipitation: int)->None:
        self.time: str = time
        self.screenTemperature: float = screenTemperature
        self.maxScreenAirTemp: float = maxScreenAirTemp
        self.minScreenAirTemp: float = minScreenAirTemp
        self.screenDewPointTemperature: float = screenDewPointTemperature
        self.feelsLikeTemperature: float = feelsLikeTemperature
        self.windSpeed10m: float = windSpeed10m
        self.windDirectionFrom10m: int = windDirectionFrom10m
        self.windGustSpeed10m: float = windGustSpeed10m
        self.max10mWindGust: float = max10mWindGust
        self.visibility: int = visibility
        self.screenRelativeHumidity: float = screenRelativeHumidity
        self.mslp: int = mslp
        self.uvIndex: int = uvIndex
        self.significantWeatherCode: int = significantWeatherCode
        self.precipitationRate: float = precipitationRate
        self.totalPrecipAmount: float = totalPrecipAmount
        self.totalSnowAmount: float = totalSnowAmount
        self.probOfPrecipitation: int = probOfPrecipitation

class Location:
    def __init__(self, licence: str, name: str) -> None:
        self.licence: str = licence
        self.name: str = name

class FeatureProperties:
    def __init__(self, location: Location, model_run_date: str, request_point_distance: float) -> None:
        self.location: Location = location
        self.model_run_date: str = model_run_date
        self.request_point_distance: float = request_point_distance
        self.time_series: list[Datapoint] = []

class Symbol:
    symbol_def_site: str = 'http://www.opengis.net/def/uom/UCUM/'
    significant_weather_code_def_site: str = 'https://datahub.metoffice.gov.uk/'

    def __init__(self, value:  str, type: str):
        self.value: str = value  # URL
        self.type: str = type

class Unit:
    def __init__(self, label: str, symbol: Symbol):
        self.label: str = label
        self.symbol: Symbol = symbol

class Parameter:
    def __init__(self, name: str, description: str, unit: Unit):
        self.name: str = name
        self.description: str = description
        self.unit: Unit = unit

class Point:
    def __init__(self, lat: float, long: float, elev: float) -> None:
        self.latitude: float = lat
        self.longitude: float = long
        self.elevation: float = elev

class Feature:
    def __init__(self, point: Point, properties: FeatureProperties):
        self.point: Point = point
        self.properties: FeatureProperties = properties
