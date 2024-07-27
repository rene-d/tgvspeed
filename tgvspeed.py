#!/usr/bin/env python3

import requests
import subprocess

import rumps


class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super(AwesomeStatusBarApp, self).__init__("TGVSpeed")
        self.menu = ["🌎 Carte", "Aide", None]

        self.gps = None

        self.timer = rumps.Timer(self.show_speed, 2)
        self.timer.start()

    def show_speed(self, _):
        try:
            r = requests.get("https://wifi.sncf/router/api/train/gps", timeout=1.0)
            if r.status_code == 200:
                gps = r.json()
                if gps["success"] is True:
                    speed = gps["speed"]  # in m.s⁻¹
                    self.title = f"🚄 {speed * 3.6:.1f} km/h"
                    self.gps = gps
                    return
        except requests.exceptions.ReadTimeout:
            pass

        self.title = "🚄 ?"
        self.gps = None

    @rumps.clicked("🌎 Carte")
    def prefs(self, _):
        if self.gps is None:
            return

        lon = self.gps["longitude"]
        lat = self.gps["latitude"]
        zoom = 15
        url = f"https://maps.google.com/maps?ll={lat},{lon}&q={lat},{lon}&hl=fr&t=m&z={zoom}"

        subprocess.run(["open", url])

    @rumps.clicked("Aide")
    def help(self, _):

        url = "https://github.com/rene-d/tgvspeed"

        subprocess.run(["open", url])


if __name__ == "__main__":
    AwesomeStatusBarApp().run()
