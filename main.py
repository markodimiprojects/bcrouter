__author__ = "Marko Dimitrijevic, 7633863"

import time
import json
import multiprocessing as mp
from blockchainHandler import blockchainHandler
from jsonHandler import jsonHandler

"""
Allows for uploading the base snapshot and deltas in parallel
"""


def uploadTest():
    try:
        # Create parallel processes for uploading base snapshot and deltas
        p1 = mp.Process(target=baseUpload)
        p2 = mp.Process(target=deltaUpload)
        p1.start()
        p2.start()
        p1.join()
        p2.join()
    except Exception as e:
        print("Error starting parallel", str(e))


def baseUpload():
    """
    Uploads only the base snapshot
    Only used by maintainer
    """
    # Establish Routinator and Blockchain connection
    jsonH = jsonHandler()
    bcH = blockchainHandler()

    # Get base snapshot from Routinator and upload to Blockchain
    baseVRPS = jsonH.getBaseVRPS()
    bcH.addAllBaseVRPS(baseVRPS.json())


def deltaUpload():
    """
    Uploads all new deltas
    Only used by maintainer
    """
    # Establish Routinator and Blockchain connection
    jsonH = jsonHandler()
    bcH = blockchainHandler()
    # Get first delta notify json to store session and serial data
    deltaNotify = jsonH.getDeltaNotify().json()
    session = deltaNotify["session"]
    nextSerial = 1

    # This loop regularly checks, whether a new Delta is created
    # Once a new Delta gets detected, it gets uploaded to the Blockchain
    while True:
        deltaNotify = jsonH.getDeltaNotify().json()
        # If specified delta update version is reached
        if deltaNotify["serial"] == nextSerial:
            uploadDelta = jsonH.getDeltaData(session, nextSerial - 1).json()
            bcH.addDelta(uploadDelta)
            # This increment can be changed to increase the gap between delta updates
            nextSerial += 1
        time.sleep(15)


def downloadTest():
    """
    Downloads the most recent snapshot to be utilized by RTRTR
    """
    # Establish Blockchain connection
    # This can be used by any account
    bcH = blockchainHandler()
    snapshot = bcH.getNewestSnapshot()
    with open("/json/cache/vrps.json", "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=4)


def main():
    # By default, this start the base snapshot upload test
    uploadTest()
    # downloadTest()


if __name__ == '__main__':
    main()
