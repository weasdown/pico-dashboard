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

    @classmethod
    def from_dict(cls, data: dict) -> Datapoint:
        try:
            return cls(data['time'], data['screenTemperature'], data['maxScreenAirTemp'], data['minScreenAirTemp'],
                       data['screenDewPointTemperature'], data['feelsLikeTemperature'], data['windSpeed10m'], data['windDirectionFrom10m'],
                       data['windGustSpeed10m'], data['max10mWindGust'], data['visibility'], data['screenRelativeHumidity'],
                       data['mslp'], data['uvIndex'], data['significantWeatherCode'], data['precipitationRate'], data['totalPrecipAmount'],
                       data['totalSnowAmount'], data['probOfPrecipitation'],)
        except KeyError as ke:
            print(
                f'\ndata during KeyError for timepoint "{data['time']}": {data}')
            raise

class Location:
    def __init__(self, licence: str, name: str) -> None:
        self.licence: str = licence
        self.name: str = name

    @classmethod
    def from_dict(cls, data: dict) -> Location:
        return cls(data['licence'], data['name'])


class FeatureProperties:
    def __init__(self, location: Location, model_run_date: str, request_point_distance: float) -> None:
        self.location: Location = location
        self.model_run_date: str = model_run_date
        self.request_point_distance: float = request_point_distance
        self.time_series: list[Datapoint] = data_points

    @classmethod
    def from_dict(cls, data: dict) -> FeatureProperties:
        """
        Example dict:

        ```python
        {
            "requestPointDistance": 2368.8103,
            "modelRunDate": "2026-08-26T21:00Z",
            "timeSeries": [
                {
                    "time": "2026-08-26T21:00Z",
                    "screenTemperature": 18.46,
                    "maxScreenAirTemp": 19.5,
                    "minScreenAirTemp": 18.39,
                    "screenDewPointTemperature": 16.21,
                    "feelsLikeTemperature": 17.43,
                    "windSpeed10m": 4.48,
                    "windDirectionFrom10m": 53,
                    "windGustSpeed10m": 7.89,
                    "max10mWindGust": 7.89,
                    "visibility": 19320,
                    "screenRelativeHumidity": 86.96,
                    "mslp": 101250,
                    "uvIndex": 0,
                    "significantWeatherCode": 7,
                    "precipitationRate": 0.0,
                    "totalPrecipAmount": 0.0,
                    "totalSnowAmount": 0,
                    "probOfPrecipitation": 5
                },
                ...
                ]
            }
        ```
        """
        time_series_data = data['timeSeries']
        time_series: list[Datapoint] = [Datapoint.from_dict(
            point) for point in time_series_data]

        # location field may not be present
        location: Location | None = None
        try:
            location_dict: dict = data['location']
            location = Location.from_dict(location_dict)
        except KeyError as ke:
            print(f'\nWARNING: Could not get location data for feature properties')

        return cls(location=location, model_run_date=data['modelRunDate'], request_point_distance=data['requestPointDistance'], data_points=time_series)


class Symbol:
    symbol_def_site: str = 'http://www.opengis.net/def/uom/UCUM/'
    significant_weather_code_def_site: str = 'https://datahub.metoffice.gov.uk/'

    def __init__(self, value:  str, type: str):
        self.value: str = value  # URL
        self.type: str = type

    @classmethod
    def from_dict(cls, data: dict) -> Symbol:
        """
        Example dict:

        ```python
        {
            "value": "http://www.opengis.net/def/uom/UCUM/",
            "type": "mm"
        }
        ```
        """
        return cls(data['value'], data['type'])


class Unit:
    def __init__(self, label: str, symbol: Symbol):
        self.label: str = label
        self.symbol: Symbol = symbol

    @classmethod
    def from_dict(cls, data: dict) -> Unit:
        """
        Example dict:

        ```python
        {
            "label": "millimetres",
            "symbol": {
                "value": "http://www.opengis.net/def/uom/UCUM/",
                "type": "mm"
            }
        }
        ```
        """
        return cls(data['label'], Symbol.from_dict(data['symbol']))


class Parameter:
    def __init__(self, name: str, description: str, unit: Unit):
        self.name: str = name
        self.description: str = description
        self.unit: Unit = unit

    @classmethod
    def from_tuple(cls, data: tuple) -> Parameter:
        """
        Example data:

        ```python
        "totalSnowAmount": {
            "type": "Parameter",
            "description": "Total Snow Amount Over Previous Hour",
            "unit": {
                "label": "millimetres",
                "symbol": {
                    "value": "http://www.opengis.net/def/uom/UCUM/",
                    "type": "mm"
                }
            }
        }
        ```
        """
        name: str = data[0]
        values: dict = data[1]
        return cls(name, values['description'], Unit.from_dict(values['unit']))

    def __repr__(self) -> str:
        return f'{self.description} ({self.unit.symbol.type})'

class Point:
    def __init__(self, lat: float, long: float, elev: float) -> None:
        self.latitude: float = lat
        self.longitude: float = long
        self.elevation: float = elev


class Feature:
    def __init__(self, point: Point, properties: FeatureProperties):
        self.point: Point = point
        self.properties: FeatureProperties = properties

    @classmethod
    def from_dict(cls, data: dict) -> Feature:
        """
        Example dict:

        ```python
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    1.2521,
                    51.8319,
                    0.0
                ]
            },
            "properties": {
                "requestPointDistance": 2368.8103,
                "modelRunDate": "2026-08-26T21:00Z",
                "timeSeries": [
                    {
                        "time": "2026-08-26T21:00Z",
                        "screenTemperature": 18.46,
                        "maxScreenAirTemp": 19.5,
                        "minScreenAirTemp": 18.39,
                        "screenDewPointTemperature": 16.21,
                        "feelsLikeTemperature": 17.43,
                        "windSpeed10m": 4.48,
                        "windDirectionFrom10m": 53,
                        "windGustSpeed10m": 7.89,
                        "max10mWindGust": 7.89,
                        "visibility": 19320,
                        "screenRelativeHumidity": 86.96,
                        "mslp": 101250,
                        "uvIndex": 0,
                        "significantWeatherCode": 7,
                        "precipitationRate": 0.0,
                        "totalPrecipAmount": 0.0,
                        "totalSnowAmount": 0,
                        "probOfPrecipitation": 5
                    },
                    ...
                ]
            }
        }
        ```
        """
        coords = data['geometry']['coordinates']
        point: Point = Point(coords[0], coords[1], coords[2])

        properties_dict: dict = data['properties']
        properties: FeatureProperties = FeatureProperties.from_dict(
            properties_dict)

        return cls(point, properties)

    def __repr__(self) -> str:
        return f'Feature for {self.point.longitude}, {self.point.latitude}, run at {self.properties.model_run_date}'


class SpotForecastFeatureCollection:
    def __init__(self, feature: Feature, parameters: list[Parameter]) -> None:
        self.feature: Feature = feature
        self.parameters: list[Parameter] = parameters

    @classmethod
    def from_dict(cls, data: dict) -> SpotForecastFeatureCollection:
        parameters_data: dict[str, dict] = data['parameters'][0]
        parameter_items = list(parameters_data.items())

        # raise NotImplementedError(
        #     'SpotForecastFeatureCollection.from_dict() is not yet fully implemented')
        parameters = [Parameter.from_tuple(param_data)
                      for param_data in parameter_items]
        return cls(Feature.from_dict(data['features'][0]), parameters)
