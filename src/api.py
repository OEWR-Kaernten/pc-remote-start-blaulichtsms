import json
from fastapi.routing import APIRoute
import inspect
import re
import requests
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from decouple import config
import datetime
import humanize
from src.utils import Utilities
from src.models import APIStatus, AlarmState
from fastapi_utils.tasks import repeat_every
from src.blaulichtsms import BlaulichtSMSAPI
import pytz

utc=pytz.UTC

version = config("VERSION", default="DEV", cast=str)
start_time = datetime.datetime.now()
logger = Utilities.setup_logger()
token = config("BLAULICHT_DASHBOARD_TOKEN", cast=str) # intentional crash if no token set!
blaulichtsms = BlaulichtSMSAPI(token)
last_alarm = datetime.datetime.now(tz=utc) - datetime.timedelta(minutes=15)

if version == "%VER%":
    version = "DEV"

app = FastAPI(
    title="BlaulichtSMS Alarm Monitoring",
    version=version,
)

@app.get("/",
         summary="Check service status",
         response_model=APIStatus,
         tags=["Status"])
async def root() -> APIStatus:
    time_delta = datetime.datetime.now() - start_time
    output_time = humanize.naturaldelta(time_delta)
    return APIStatus(version=version, uptime=output_time)


@app.get("/wake-device/{mac_address}")
async def wake_device_custom_mac(mac_address: str | None = None):
    print("Hello world!")

@app.get("/wake-device/")
async def wake_device(mac_address: str | None = None):
    print("Hello world!")

@app.get("/query-alarm/", response_model=AlarmState, summary="Query for new alarm. If new alarm found, wake PC")
async def check_for_new_alarm() -> AlarmState:
    global last_alarm
    alarms = blaulichtsms.get_alarm_state()
    print(alarms)
    new_alarm_found=False

    for c_alarm in alarms.alarms:
        print(f"LOCAL: {c_alarm.alarmDate}")
        print(f"{last_alarm} < {c_alarm.alarmDate})")
        print(last_alarm < c_alarm.alarmDate)
        if last_alarm < c_alarm.alarmDate:
            new_alarm_found = True
            last_alarm = c_alarm.alarmDate
            break

    if new_alarm_found:
        print("TODO: start PC")

    return AlarmState(found_new_alarm=new_alarm_found, alarms=alarms)

@app.on_event("startup")
@repeat_every(seconds=config("CHECK_INTERVAL", cast=int, default=30))
async def periodically_check_alarm():
    await check_for_new_alarm()