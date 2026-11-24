#!/usr/bin/env python3

import subprocess
import http.client
import requests
import hashlib
import os

endpoint="https://api.beeper.com/desktop/download/linux/x64/stable/com.automattic.beeper.desktop"

current="4.3.340-x86_64"

# get headers of the download url to get the "real" version download url
conn = http.client.HTTPSConnection('api.beeper.com')
conn.request('GET', '/desktop/download/linux/x64/stable/com.automattic.beeper.desktop')
response = conn.getresponse()
loc=response.getheader("Location")

# parse version
urlarr=loc.split("/")
fname=urlarr[len(urlarr)-1]
print(fname)
version=fname.lower().replace("beeper-", "").replace(".appimage", "")
print(version)

def github_output(key, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as fh:
            fh.write(f"{key}={value}\n")

if version == current:
    print("no new version.")
    github_output("changed", "false")
    exit()

# update strings in files (build.yml uses github.ref_name, no version string there)
update_files=["autobuild.py", "com.beeper.beeper.yaml"]
for name in update_files:
    sed_expr=f"sed -e 's,{current},{version},' -i {name}"
    print(sed_expr)
    subprocess.run(sed_expr, shell=True)

# update shasum in com.beeper.beeper.yaml
open('beeper.appimage', 'wb').write(requests.get(loc).content)

sha256_hash = hashlib.sha256()
with open('beeper.appimage',"rb") as f:
    for byte_block in iter(lambda: f.read(4096),b""):
        sha256_hash.update(byte_block)
    shasum=sha256_hash.hexdigest()
    sed_expr=f"sed -e 's,sha256: .*,sha256: {shasum},' -i com.beeper.beeper.yaml"
    subprocess.run(sed_expr, shell=True)

statcode=subprocess.run("git status|grep 'nothing to commit'", shell=True)
if statcode.returncode!=0:
    print("Commiting")
    commit=f"git commit -am 'autobuild for {version}'"
    tagetc=f"git tag {version}; git push; git push origin {version}"

    commit_out=subprocess.run(commit, shell=True)
    tag_out=subprocess.run(tagetc, shell=True)
    print(f"Commit: {commit_out.returncode}, tag: {tag_out.returncode}")
    github_output("changed", "true")
    github_output("version", version)
else:
    github_output("changed", "false")
