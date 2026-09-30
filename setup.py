"""Run once: downloads the prebuilt Python-on-WASM runtime into ./runtime"""
import os, urllib.request, zipfile

URL = ("https://github.com/vmware-labs/webassembly-language-runtimes/releases/download/"
       "python/3.11.1+20230127-c8036b4/python-aio-3.11.1.zip")
HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, "runtime")
os.makedirs(DEST, exist_ok=True)
zpath = os.path.join(DEST, "py.zip")

print("Downloading python.wasm runtime (~25MB)...")
urllib.request.urlretrieve(URL, zpath)
with zipfile.ZipFile(zpath) as z:
    z.extractall(DEST)
os.remove(zpath)
print("Done. Contents of runtime/:", os.listdir(DEST))