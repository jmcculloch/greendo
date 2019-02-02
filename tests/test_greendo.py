import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import greendo

USERNAME='TODO'
PASSWORD='TODO'
client = greendo.Client(USERNAME, PASSWORD)
devices = client.devices[-1]

def test_door_status():
    print(devices.door.door_status())
    assert devices.door.door_status() == greendo._Door.CLOSED

def test_light_status():
    print(devices.light.on())
    assert devices.light.on() == False

def test_turn_light_on():
    client.send_command(devices.cmd_light(False))
