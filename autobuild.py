#!/usr/bin/env python3

import subprocess
import http.client

endpoint="https://api.beeper.com/desktop/download/linux/x64/stable/com.automattic.beeper.desktop"

current="https://beeper-desktop.download.beeper.com/builds/Beeper-4.0.494.AppImage"

curl_call=subprocess.run(["curl", "-si", endpoint], capture_output=True)

ver=curl_call.stdout

conn = http.client.HTTPSConnection('api.beeper.com')
conn.request('GET', '/desktop/download/linux/x64/stable/com.automattic.beeper.desktop')
response = conn.getresponse()
loc=response.getheader("Location")

if loc != current:
    subprocess.run(["sed", "-e", f"'s,{current},{loc},'", "-i", "autobuild.py"])
else:
    print("no new version.")
    exit()

urlarr=loc.split("/")
fname=urlarr[len(urlarr)-1]
print(fname)
version=fname.lower().replace("beeper-", "").replace(".appimage", "")
print(version)
