import time
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


"""
Uploads the base snapshot
"""


def baseUpload():
    # Establish Routinator and Blockchain connection
    jsonH = jsonHandler()
    bcH = blockchainHandler()

    # Get base snapshot from Routinator and upload to Blockchain
    baseVRPS = jsonH.getBaseVRPS()
    bcH.addAllBaseVRPS(baseVRPS.json())


"""
Uploads all new deltas
"""


def deltaUpload():
    # Establish Routinator and Blockchain connection
    jsonH = jsonHandler()
    bcH = blockchainHandler()
    # Get first delta notify json to store session and serial data
    deltaNotify = jsonH.getDeltaNotify().json()
    session = deltaNotify["session"]
    nextSerial = 1

    # This loop regularly checks, when a new Delta is created
    # Once a new Delta gets detected, it gets uploaded to the Blockchain
    while True:
        deltaNotify = jsonH.getDeltaNotify().json()
        print("Current delta serial: %s" % (deltaNotify["serial"]))
        if deltaNotify["serial"] == nextSerial:
            uploadDelta = jsonH.getDeltaData(session, nextSerial - 1).json()
            bcH.addDelta(uploadDelta)
            nextSerial += 1
        time.sleep(15)

def downloadTest():
    bcH = blockchainHandler()
    snapshot = bcH.getNewestSnapshot()
    print(snapshot)


def main():
    uploadTest()
    #downloadTest()


if __name__ == '__main__':
    main()
