#!/usr/bin/env python3

# Pepita utilise Socket.IO 3 (et donc la version du module Python...)
# pip install python-socketio==4.6.1

import json
import asyncio
import socketio
from pathlib import Path


class PepitaNamespace(socketio.AsyncClientNamespace):

    async def on_connect(self):
        print("on_connect")

    async def on_disconnect(self):
        print("on_disconnect")

    async def on_gps(self, data):
        print(data)

    async def on_trainDetails(self, data):
        print(data)

    async def on_connected_devices(self, data):
        print(data)

    async def on_data_consumption(self, data):
        print(data)


    # async def trigger_event(self, event, *args):
    #     print(event, args)
    #     if len(args) > 0:
    #         Path(event).with_suffix(".json").write_text(json.dumps(args[0], indent=2))
    #         pass

    """
    Liste exhaustive des events (trouvée dans le code javascript du frontend web):
        gps
        connected_devices
        internet_link_quality
        data_consumption
        trainDetails
        trainGraph
        trainCoverageGraph
        modulesConfiguration
        bar_attendance
        updateHistory
        updateUsers
        updateRooms
        addMessage
        updateMessage
        deleteMessage
        chatReady
        requestInput
    """


sio = socketio.AsyncClient()

sio.register_namespace(PepitaNamespace("/router/api/pepita"))


async def start_server():
    await sio.connect("https://wifi.sncf/")
    await sio.wait()


if __name__ == "__main__":
    asyncio.run(start_server())
