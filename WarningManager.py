from datetime import datetime, timezone
import requests
import logging
import Nyon_Util

class Warning:
    """
    This is an object to contain and deal with warning data.
    """

    def __init__(self, data: dict) -> None:

        logger = logging.getLogger(Nyon_Util.get_custom_logger_name())
        
        self._debug_raw_data = data["debug_raw_data"]
        self.id: str = data["id"]
        # self.replaces: str = data["replaces"]
        self.area_desc: str = data["area_description"]
        self.sent_time: datetime = datetime.strptime(data["sent_time"], "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)
        self.effective_time: datetime = datetime.strptime(data["effective_time"], "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)
        self.expiration_time: datetime = datetime.strptime(data["expiration_time"], "%Y-%m-%dT%H:%M:%S%z").astimezone(timezone.utc)
        self.status: str = data["status"]
        self.severity: str = data["severity"]
        self.event_type: str = data["event_type"]
        self.message_type: str = data["message_type"]
        self.headline: str = data["headline"]
        self.description: str = data["description"]
        self.instruction: str = data["instruction"]
        self.wind_gust: str = data["max_wind_gust"]
        self.wind_threat: str = data["wind_threat"]
        self.hail_size: str = data["max_hail_size"]
        self.hail_threat: str = data["hail_threat"]
        self.tornado_detection: str = data["tornado_detection"]
        self.storm_threat: str = data["storm_threat"]

    def dump_info(self) -> dict:

        return_dict = {}

        for attr, val in self.__dict__.items():

            return_dict[attr] = val

        return return_dict

    def __eq__(self, other: 'Warning') -> bool:

        if not isinstance(other, Warning):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:

        return hash(self.id)

class WarningManager:
    """
    Manager class for managing warning, Light at the moment, Will add more later.
    """

    MONITORED_WARNING_TYPES = ['Tornado Warning', 'Severe Thunderstorm Warning', 'Flash Flood Warning']

    def __init__(self, url: str = "https://api.weather.gov/alerts/active", user_agent: dict = {"User-Agent": "Name: AutoBrad, Desc: Discord Bot, Contact: quontex@hotmail.com"}) -> None:
        
        self.logger = logging.getLogger(Nyon_Util.get_custom_logger_name())

        self.api_url: str = url
        self.user_agent: str = user_agent
        self.warning_set: set[Warning] = {Warning(self._extract_relevant_data(alert)) for alert in self._poll_warning_data()}

    def _poll_warning_data(self) -> list[dict]:

        try:
            response = requests.get(self.api_url, headers=self.user_agent)
            self.logger.info(f"Fetching Warning Data")
        except TimeoutError:
            self.logger.error(f"API Timeout")
            return []
        self.logger.info(f"Successfully fetched warning data")
        data = response.json()
        filtered_alerts = [alert for alert in data['features'] if alert['properties']['event'] in self.MONITORED_WARNING_TYPES]

        return filtered_alerts

    def _extract_relevant_data(self, warning) -> dict:
        properties = warning.get('properties', {})

        warning_data = {
            'debug_raw_data': properties,
            'id': properties.get('@id'),
            # 'replaces': properties.get('references', {}).get('@id', None),
            'area_description': properties.get('areaDesc'),
            'sent_time': properties.get('sent'),
            'effective_time': properties.get('effective'),
            'expiration_time': properties.get('expires'),
            'status': properties.get('status'),
            'severity': properties.get('severity'),
            'event_type': properties.get('event'),
            'message_type': properties.get('messageType'),
            'headline': properties.get('headline'),
            'description': properties.get('description'),
            'instruction': properties.get('instruction'),
            'max_wind_gust': properties.get('parameters', {}).get('maxWindGust', [None])[0],
            'wind_threat': properties.get('parameters', {}).get('windThreat', [None])[0],
            'max_hail_size': properties.get('parameters', {}).get('maxHailSize', [None])[0],
            'hail_threat': properties.get('parameters', {}).get('hailThreat', [None])[0],
            'tornado_detection': properties.get('parameters', {}).get('tornadoDetection', [None])[0],
            'storm_threat': properties.get('parameters', {}).get('thunderstormDamageThreat', ["Standard"])[0]
        }
        
        return warning_data

    def update(self) -> None:

        now = datetime.now()

        self.warning_set: set[Warning] = {Warning(self._extract_relevant_data(alert)) for alert in self._poll_warning_data()}

        # expired_warnings = {warning for warning in self.warning_set if datetime.now().timestamp() - warning.expiration_time.timestamp() <= 0}
        # self.warning_set -= expired_warnings

        current_warnings: set[Warning] = set()

        for warning in self.warning_set:
            tstmp1 = datetime.now().timestamp()
            tstmp2 = warning.expiration_time.timestamp()

            if tstmp1 - tstmp2 < 0:
                current_warnings.add(warning)

        self.warning_set = current_warnings

if __name__ == "__main__":
    print("This is a lib file")