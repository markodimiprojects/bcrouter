__author__ = "Marko Dimitrijevic, 7633863"

import time
import requests
import os
from dotenv import load_dotenv


class jsonHandler:
    """
    @author: Marko Dimitrijevic, 7633863

    This class is responsible for fetching data from the Routinator connection
    """

    def __init__(self):
        load_dotenv()
        self.httpURL = os.getenv("HTTPURL_TEST")+"/"  # URL of the Routinator HTTP endpoint
        # Initialization finishes once Routinator fetches all VRPs
        while True:
            time.sleep(10)
            jsonReq = requests.get(self.httpURL + 'json')
            # Seen codes
            # 503 - Setup stage
            # 200 - Setup complete
            if jsonReq.status_code == 200:
                break

    def httpGet(self, path, payload):
        """
        Fetch the data of a HTTP request

        :param path: Subpath of the HTTP request
        :type path: String
        :param payload: Addition parameters added through the payload
        :type payload: Dict
        :return: Request data
        :rtype: Response
        """
        try:
            return requests.get(self.httpURL + path, params=payload)
        except Exception as e:
            print("Error fetching HTTP request: ", str(e))

    def getBaseVRPS(self):
        """
        Fetch the most recent snapshot. At the start of Routinator this returns the base snapshot
        :return: Request data
        :rtype: Response
        """
        try:
            return self.httpGet("json", {})
        except Exception as e:
            print("Error fetching snapshot: ", str(e))

    def getDeltaNotify(self):
        """
        Fetch the most recent delta notification
        :return: Request data
        :rtype: Response
        """
        try:
            print("Getting Delta Notify")
            deltaNotification = self.httpGet("json-delta/notify", {})
            return deltaNotification
        except Exception as e:
            print("Error fetching delta notify: ", str(e))

    def getDeltaData(self, session, serial):
        """
        Fetch the most recent delta

        :param session: Session ID
        :type session: int
        :param serial: Serial ID, this ID defines, from which snapshot the delta is built
        :type serial: int
        :return: Request data
        :rtype: Response
        """
        try:
            print("Getting Delta data")
            deltaReq = self.httpGet("json-delta", {"session": session, "serial": serial})
            return deltaReq
        except Exception as e:
            print("Error fetching delta data: ", str(e))
