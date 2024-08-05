#!/usr/bin/env python3

import argparse
import json
import subprocess

import requests
import rumps


class TgvSpeedStatusBarApp(rumps.App):

    def __init__(self, simulation=False):
        super(TgvSpeedStatusBarApp, self).__init__("TGVSpeed")

        if simulation:
            self.url_gps = "http://localhost:8000/gps.json"
        else:
            self.url_gps = "https://wifi.sncf/router/api/train/gps"

        self.menu = ["Statut", "Aide", None]

        self.gps = None
        self.last_error = None

        self.title = "🚄 🔴"

        m = rumps.MenuItem("🚆 Voyage", None)
        self.menu.insert_before("Statut", m)

        m = rumps.MenuItem("🌎 Carte", None)
        self.menu.insert_before("Statut", m)

        self.timer = rumps.Timer(self.show_speed, 2)
        self.timer.start()

    def show_speed(self, _):
        try:
            r = requests.get(self.url_gps, timeout=1.0)
            r.raise_for_status()

            self.last_error = None

            gps = r.json()
            if gps["success"] is True:
                self.set_gps(gps)
                return

        except requests.exceptions.RequestException as e:
            self.last_error = str(e)

        self.set_gps(None)

    def set_gps(self, gps):
        """
        Actualise la position GPS et le menu.
        """

        if gps is None:
            if self.gps is not None:
                self.menu["🚆 Voyage"].set_callback(None)
                self.menu["🌎 Carte"].set_callback(None)
                self.title = "🚄 🔴"
                self.gps = None

        else:
            if self.gps is None:
                self.menu["🚆 Voyage"].set_callback(self.journey)
                self.menu["🌎 Carte"].set_callback(self.map)

            speed = gps["speed"]  # in m.s⁻¹
            self.title = f"🚄 {speed * 3.6:.1f} km/h"
            self.gps = gps

    def journey(self, _):
        """
        Affiche le voyage sur le portail SNCF.
        """
        if self.gps is None:
            return
        url = "https://wifi.sncf/fr/journey"

        subprocess.run(["open", url])

    def map(self, _):
        """
        Affiche la position actuelle dans Google Maps.
        """
        if self.gps is None:
            return

        lon = self.gps["longitude"]
        lat = self.gps["latitude"]
        zoom = 15
        url = f"https://maps.google.com/maps?ll={lat},{lon}&q={lat},{lon}&hl=fr&t=m&z={zoom}"

        subprocess.run(["open", url])

    @rumps.clicked("Statut")
    def status(self, _):
        """
        Affiche la requête de position ou le dernier message d'erreur.
        """
        if self.last_error:
            rumps.alert("Erreur", self.last_error, icon_path="480px-Robot_icon_broken.svg.png")
        if self.gps:
            rumps.alert("GPS", json.dumps(self.gps, indent="\t"), icon_path="gps.png")

    @rumps.clicked("Aide")
    def help(self, _):
        """
        Lien GitHub vers le code soure.
        """

        url = "https://github.com/rene-d/tgvspeed"

        subprocess.run(["open", url])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--local", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    rumps.debug_mode(args.verbose)

    TgvSpeedStatusBarApp(simulation=args.local).run()
