#!/usr/bin/env python

# Copyright 2017 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provide a basic client for accessing functionality for the RYOBI GDO.

Can be used on the command line by specifying a command and optional values for it, e.g.,

> python greendo.py door open
> python greendo.py light off
> python greendo.py status door

See help for more details.
"""

import greendo
import json
import argparse

from getpass import getpass
from contextlib import closing

def main():
    ap = argparse.ArgumentParser(prog="greendo")
    ap.add_argument("--email", "-u", type=str, help="Email address registered with the GDO app. Default: request from stdin.")
    ap.add_argument("--pwd", "-p", type=str, help="Password for the registered email. Default: request from stdin.")
    ap.add_argument("--dry", "-n", action="store_true", help="Dry run - don't execute commands, just display them")
    ap.add_argument("--dev", "-d", type=int, default=0, help="Door opener device index, if you have more than one.")
    sub_ap = ap.add_subparsers(dest="target", help="Commands")

    ap_status = sub_ap.add_parser("status", help="Output status for a given subsystem.")
    ap_status.add_argument("thing", choices=("config", "charger", "door", "light", "fan"),
                           help="Get status for the given subsystem.")

    ap_door = sub_ap.add_parser("door", help="Manipulate the door: open, close, preset.")
    ap_door.add_argument("cmd", choices=("open", "close", "preset"))

    ap_motion = sub_ap.add_parser("motion", help="Turn the motion sensor on or off.")
    ap_motion.add_argument("set", choices=("on", "off"))

    ap_light = sub_ap.add_parser("light", help="Turn the light on or off.")
    ap_light.add_argument("set", choices=("on", "off"))

    ap_light_timer = sub_ap.add_parser("lighttimer", help="Set the number of minutes for the light timer.")
    ap_light_timer.add_argument("minutes", type=int)

    ap_fan = sub_ap.add_parser("fan", help="Set fan to integer speed 0-100 (0 is off)")
    ap_fan.add_argument("speed", type=int)

    ap_vacation = sub_ap.add_parser("vacation", help="Turn vacation mode on or off.")
    ap_vacation.add_argument("set", choices=("on", "off"))

    ap_preset_pos = sub_ap.add_parser("preset", help="Set the preset position in integer inches.")
    ap_preset_pos.add_argument("inches", type=int)

    args = ap.parse_args()

    email = args.email
    pwd = args.pwd
    if args.email is None:
        email = input("email: ").strip()
    if args.pwd is None:
        pwd = getpass("password: ").strip()

    with closing(greendo.Client(email, pwd)) as client:
        device = client.devices[max(0, min(args.dev, len(client.devices)))]
        cmd = None
        if args.target == "status":
            thing = args.thing
            if thing == "config":
                print("Session:\n", json.dumps(client.session.data, indent=2))
                print("Devices:\n", json.dumps([{"meta": d.meta, "data": d.data} for d in client.devices], indent=2))
            elif thing == "charger":
                print(json.dumps({
                    "level": device.charger.level()
                }, indent=2))
            elif thing == "door":
                door = device.door
                print(json.dumps({
                    "status": door.door_status(),
                    "error": door.door_error(),
                    "pos": door.door_pos(),
                    "max": door.door_max(),
                    "preset": door.preset_pos(),
                    "motion": door.motion(),
                    "alarm": door.alarm(),
                    "motor": door.motor(),
                    "sensor": door.sensor(),
                    "vacation": door.vacation(),
                }, indent=2))
            elif thing == "light":
                light = device.light
                print(json.dumps({
                    "light": light.on(),
                    "timer": light.timer(),
                }, indent=2))
            elif thing == "fan":
                print(json.dumps({
                    "speed": device.fan.speed(),
                }, indent=2))
            return

        if args.target == "door":
            if args.cmd == "open":
                cmd = device.cmd_open()
            elif args.cmd == "close":
                cmd = device.cmd_close()
            else:
                cmd = device.cmd_preset()
        elif args.target == "motion":
            cmd = device.cmd_motion(args.set == "on")
        elif args.target == "light":
            cmd = device.cmd_light(args.set == "on")
        elif args.target == "lighttimer":
            cmd = device.cmd_lighttimer(max(0, args.minutes))
        elif args.target == "fan":
            cmd = device.cmd_fan(max(0, min(100, args.speed)))
        elif args.target == "vacation":
            cmd = device.cmd_vacation(args.set == "on")
        elif args.target == "preset":
            cmd = device.cmd_preset(max(0, args.inches))

        if args.dry:
            print("Dry Run:")
            print(json.dumps(cmd, indent=2))
            return

        print("Request to {}:".format(client.API_URL_SOCKET))
        print(json.dumps(cmd, indent=2))

        result = client.send_command(cmd)
        print("Response:")
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
