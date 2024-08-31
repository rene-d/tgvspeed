#!/usr/bin/env python3


import argparse
import json
import subprocess
import logging
from datetime import datetime
import requests
import rumps
from Foundation import NSMenuItemBadge

TITLE_UNAVAILABLE = "🚉"


class TgvSpeedStatusBarApp(rumps.App):

    def __init__(self, simulation=False):
        super(TgvSpeedStatusBarApp, self).__init__("TGVSpeed")

        if simulation:
            self.url_gps = "http://localhost:8000/gps.json"
        else:
            self.url_gps = "https://wifi.sncf/router/api/train/gps"

        self.menu_voyage = rumps.MenuItem("Voyage", None, icon="train.png", dimensions=(22, 22))
        self.menu_carte = rumps.MenuItem("Carte (Google)", None, icon="map.png", dimensions=(22, 22))

        self.menu = [
            self.menu_voyage,
            {"Arrêts": [None]},
            self.menu_carte,
            None,
            rumps.MenuItem("Statut", self.statut),
            rumps.MenuItem("Aide", self.aide),
            None,
        ]

        self.stops = self.menu["Arrêts"]

        self.stops.set_icon("destination.png", dimensions=(22, 22))

        self.gps = None
        self.details = None
        self.last_error = None

        self.title = TITLE_UNAVAILABLE

        self.timer_gps = rumps.Timer(self.show_speed, 2)
        self.timer_gps.start()

        self.timer_details = rumps.Timer(self.show_details, 30)
        self.timer_details.start()

    def show_details(self, timer):
        logging.debug(f"show_details {timer}")
        try:
            r = requests.get("https://wifi.sncf/router/api/train/details", timeout=1.0)
            r.raise_for_status()
            self.set_details(r.json())
        except Exception:
            self.set_details(None)

    def show_speed(self, timer):
        logging.debug(f"show_speed {timer}")
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
        self.set_details(None)

    def set_details(self, details):
        """
        Actualise le numéro de train, les étapes et le menu.
        """

        for stop in details.get("stops", []):
            progress = stop.get("progress")
            if progress:
                stop["is_done"] = progress["progressPercentage"] != 0
                progress["progressPercentage"] = 0
                progress["traveledDistance"] = 0
                progress["remainingDistance"] = 0
            else:
                stop["is_done"] = False

        if self.details != details:
            self.details = details

            if details:

                self.stops.title = f'{details["carrier"]} {details["number"]}'
                self.stops.clear()

                for stop in details["stops"]:

                    real_date = datetime.fromisoformat(stop["realDate"])
                    real_date = real_date.astimezone(None)
                    real_date = real_date.strftime("%H:%M")

                    label = f'{real_date} {stop["label"]}'

                    m = rumps.MenuItem(
                        label,
                        callback=(
                            None
                            if stop["is_done"]
                            else lambda _: subprocess.run(["open", f"https://wifi.sncf/fr/stops/{stop['code']}"])
                        ),
                    )

                    if stop["isDelayed"]:
                        b = NSMenuItemBadge.alloc().initWithString_(f"retard: {stop['delay']} min")
                        m._menuitem.setBadge_(b)
                        m._menuitem.setToolTip_(stop["delayReason"])

                    self.stops.add(m)

    def set_gps(self, gps):
        """
        Actualise la position GPS et le menu.
        """

        if gps is None:
            if self.gps is not None:
                self.menu_voyage.set_callback(None)
                self.menu_carte.set_callback(None)
                self.title = TITLE_UNAVAILABLE
                self.gps = None

        else:
            if self.gps is None:
                self.menu_voyage.set_callback(self.voyage)
                self.menu_carte.set_callback(self.carte)

            speed = gps["speed"]  # in m.s⁻¹
            self.title = f"🚄 {speed * 3.6:.1f} km/h"
            self.gps = gps

    def voyage(self, _):
        """
        Affiche le voyage sur le portail SNCF.
        """
        if self.gps is None:
            return
        url = "https://wifi.sncf/fr/journey"

        subprocess.run(["open", url])

    def carte(self, _):
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

    def statut(self, _):
        """
        Affiche la requête de position ou le dernier message d'erreur.
        """
        if self.last_error:
            rumps.alert("Erreur", self.last_error, icon_path="480px-Robot_icon_broken.svg.png")
        if self.gps:
            rumps.alert("GPS", json.dumps(self.gps, indent="\t"), icon_path="gps.png")

    def aide(self, _):
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

    logging.basicConfig(
        format="\033[2m%(asctime)s - %(levelname)s - %(message)s\033[0m",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    rumps.debug_mode(args.verbose)

    TgvSpeedStatusBarApp(simulation=args.local).run()
