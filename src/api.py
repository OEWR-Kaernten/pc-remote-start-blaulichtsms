import json
from typing import Dict, Any

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
from src.models import APIStatus, AlarmState, Status
from fastapi_utils.tasks import repeat_every
from src.blaulichtsms import BlaulichtSMSAPI
from src.device import Device
import pytz

utc = pytz.UTC

version = config("VERSION", default="DEV", cast=str)
start_time = datetime.datetime.now()
logger = Utilities.setup_logger()
# intentional crash if no token set!
token = config("BLAULICHT_DASHBOARD_TOKEN", cast=str)
if config("OEWR", default=False, cast=bool):
    default_device = Device(mac_address="None")
else:
    default_device = Device(
        mac_address=config("MAC_ADDRESS_DEFAULT_DEVICE", cast=str)
    )  # intentional crash if no mac set!
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


@app.get("/wake-device/{mac_address}",
         response_model=Status,
         tags=["Wake on Lan"])
async def wake_device_custom_mac(mac_address: str) -> Status:
    dev = Device(mac_address=mac_address)
    logger.info(f"Started device {dev.mac_address}")
    return dev.start_device()

@app.get("/wake-device/move-mouse/",
         response_model=Status,
         tags=["Move the Mouse"])
async def force_move_mouse() -> dict[str, Any]:
    dev = Device(mac_address="None")
    logger.info(f"Mouse moved")
    return {"success": dev.move_mouse()}


@app.get("/wake-device/",
         response_model=Status,
         tags=["Wake Device"])
async def wake_device() -> Status:
    if config("OEWR", default=False, cast=bool):
        logger.info(f"Started device using mouse movement")
        return {"success": default_device.move_mouse()}
    else:
        logger.info(f"Started device {default_device.mac_address}")
        return default_device.start_device()


@app.get("/query-alarm/", response_model=AlarmState, summary="Query for new alarm. If new alarm found, wake PC")
async def check_for_new_alarm() -> AlarmState:
    global last_alarm
    alarms = blaulichtsms.get_alarm_state()
    logger.debug(alarms)
    new_alarm_found = False

    for c_alarm in alarms.alarms:
        if last_alarm < c_alarm.alarmDate:
            logger.info(f"Found new alarm, starting device!")
            new_alarm_found = True
            last_alarm = c_alarm.alarmDate
            break

    if new_alarm_found:
        await wake_device()

    return AlarmState(found_new_alarm=new_alarm_found, alarms=alarms)


@app.on_event("startup")
@repeat_every(seconds=config("CHECK_INTERVAL", cast=int, default=30))
async def periodically_check_alarm():
    logger.debug("Checking for new alarms...")
    await check_for_new_alarm()
