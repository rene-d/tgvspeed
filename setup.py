"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ["tgvspeed.py"]
DATA_FILES = ["480px-Robot_icon_broken.svg.png", "gps.png", "train.png", "map.png", "destination.png"]
OPTIONS = {
    "iconfile": "icon.icns",
    "plist": {
        "CFBundleShortVersionString": "0.1.0",
    },
}
setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app", "rumps", "requests"],
)
