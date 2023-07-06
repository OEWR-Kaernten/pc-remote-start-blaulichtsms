import requests
from src.models import *
import pytz
import datetime


BASE_URL = "https://api.blaulichtsms.net/blaulicht/api/"
ALARM_URL = BASE_URL + "alarm/v1/dashboard/"
utc = pytz.UTC


class BlaulichtSMSAPI:
    def __init__(self, token):
        self._token = token

    def get_alarm_state(self) -> BlaulichtSMSAPIAlarmResponse:
        req = requests.get(ALARM_URL+self._token)
        alarm_list = list()
        if req.status_code == 200:
            for c_alarm in req.json()["alarms"]:
                localized_time = utc.localize(datetime.datetime.strptime(
                    c_alarm["alarmDate"], "%Y-%m-%dT%H:%M:%S.%fZ"))
                alarm_list.append(BlaulichtSMSAPIAlarmSingleResponse(
                    alarmDate=localized_time, alarmText=c_alarm["alarmText"]))
        else:
            print(f"Status code: {req.status_code}")
        return BlaulichtSMSAPIAlarmResponse(alarms=alarm_list)
