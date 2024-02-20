import time
import requests
import os
from dotenv import load_dotenv

class jsonHandler:

    def __init__(self):
        # Initialization finishes once Routinator fetches all VRPs
        load_dotenv()
        self.httpURL = os.getenv("HTTPURL_TEST")
        print("Setting up routinator")
        # Spinlock waiting for proper return code
        while True:
            time.sleep(10)
            jsonReq = requests.get(self.httpURL+'json')
            # Seen codes
            # 503 - Setup stage
            # 200 - Setup complete
            if jsonReq.status_code == 200:
                break

    """
    Get the payload of a http request
    """
    def httpGet(self, url, payload):
        try:
            return requests.get(self.httpURL+url, params=payload)
        except Exception as e:
            print("Error fetching HTTP request: ", str(e))

    def getBaseVRPS(self):
        return self.httpGet("json", {})

    def getDeltaNotify(self):
        try:
            print("Getting Delta Notify")
            deltaNotification = self.httpGet("json-delta/notify", {})
            return deltaNotification
        except Exception as e:
            print("Error fetching delta notify: ", str(e))

    def getDeltaData(self, session, serial):
        try:
            print("Getting Delta data")
            deltaReq = self.httpGet("json-delta", {"session": session, "serial": serial})
            return deltaReq
        except Exception as e:
            print("Error fetching delta data: ", str(e))
