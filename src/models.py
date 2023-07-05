import typing
from typing import List, Optional

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decouple import config
import secrets

class APIStatus(BaseModel):
    message: str = "BlaulichtSMS Monitoring Service is up and running!"
    version: str
    uptime: str

class BlaulichtSMSAPIAlarmSingleResponse(BaseModel):
    alarmDate: datetime
    alarmText: str


class BlaulichtSMSAPIAlarmResponse(BaseModel):
    alarms: List[BlaulichtSMSAPIAlarmSingleResponse]

class AlarmState(BaseModel):
    found_new_alarm: bool
    alarms: BlaulichtSMSAPIAlarmResponse

class Status(BaseModel):
    success: bool