# intializing repo

import requests
from datetime import datetime, timedelta
import datetime as dt
import re
from dotenv import load_dotenv
import json
import pandas as pd
from combocurve_api_v1 import ComboCurveAuth

def getLatestScenarioOneLiner(headerData, projectIdKey, scenarioIdKey, serviceAccount, comboCurveApi):
    # FUNCTIONS
    # GET request to get Well ID to API14
    def getWellApi(wellIdComboCurve):
        authComboCurveHeaders = combocurve_auth.get_auth_headers()
        url = "https://api.combocurve.com/v1/projects/" + projectIdKey + "/wells/" + wellIdComboCurve
        responseApi = requests.request(
            "GET", url, headers=authComboCurveHeaders)
        jsonStr = responseApi.text
        dataObjBetter = json.loads(jsonStr)
        return dataObjBetter["chosenID"]

      # Get the next page URL from the response headers for pagination
    def getNextPageUrlComboCurve(response_headers: dict) -> str:
        urlHeader = response_headers.get('Link', "")
        matchComboCurve = re.findall("<([^<>]+)>;rel=\"([^\"]+)\"", urlHeader)
        for linkComboCurve, rel in matchComboCurve:
            if rel == 'next':
                return linkComboCurve
        return None

    def processNextPageUrlComboCurve(response_json):
        for i in range(0, len(response_json)):
            results = response_json[i]
            wellId = results["well"]
            output = results["output"]
            wellIdList.append(wellId)
            resultsList.append(output)

    # load enviroment variables
    load_dotenv()

    workingDir = headerData
    masterAllocationList = pd.read_excel(workingDir)

    # connect to service account
    service_account = serviceAccount
    # set API Key from enviroment variable
    api_key = comboCurveApi
    # specific Python ComboCurve authentication
    combocurve_auth = ComboCurveAuth(service_account, api_key)

    projectId = projectIdKey
    scenarioId = scenarioIdKey

    # This code chunk gets the  for given Scenerio
    # Call Stack - Get Econ Id

    authComboCurveHeaders = combocurve_auth.get_auth_headers()
    # URl econid
    url = (
        "https://api.combocurve.com/v1/projects/"
        + projectId
        + "/scenarios/"
        + scenarioId
        + "/econ-runs"
    )

    response = requests.request(
        "GET", url, headers=authComboCurveHeaders
    )  # GET request to pull economic ID for next query

    jsonStr = response.text  # convert to JSON string
    # pass to data object - allows for parsing
    dataObjBetter = json.loads(jsonStr)
    row = dataObjBetter[0]  # sets row equal to first string set (aka ID)
    econId = row["id"]  # set ID equal to variable

    # Reautenticated client
    authComboCurveHeaders = combocurve_auth.get_auth_headers()
    # set new url with econRunID, skipping zero

    urltwo = (
        "https://api.combocurve.com/v1/projects/"
        + projectId
        + "/scenarios/"
        + scenarioId
        + "/econ-runs/"
        + econId
        + "/one-liners"
    )

    resultsList = []
    wellIdList = []

    # boolean to check if there is a next page for pagination
    hasNextLink = True

    while hasNextLink:
        response = requests.request(
            "GET", urltwo, headers=authComboCurveHeaders)
        urltwo = getNextPageUrlComboCurve(response.headers)
        processNextPageUrlComboCurve(response.json())
        hasNextLink = urltwo is not None

    numEntries = len(resultsList)

    apiListBest = []
    
    print("combocurve is live")
    
    x = 5

    for i in range(0, len(wellIdList)):
        apiNumber = getWellApi(wellIdList[i])
        apiListBest.append(apiNumber)

    headerData = masterAllocationList["Chosen ID"].tolist()
    wellIdScenariosList = masterAllocationList["API 14"].tolist()

    headers = [
        "API",
        "Abandonment Date",
        "Gross Oil Well Head Volume",
        "Gross Gas Well Head Volume"
    ]

    comboCurveHeaders = [
        "Ad Valorem Tax",
        "After Income Tax Cash Flow",
        "Before Income Tax Cash Flow",
        "Depreciation",
        "Drip Condensate Differentials - 1",
        "Drip Condensate Differentials - 2",
        "Drip Condensate Gathering Expense"
    ]

    eurData = pd.DataFrame(columns=headers)

    for i in range(0, numEntries):
        row = resultsList[i]
        wellId = wellIdList[i]

        if wellId not in wellIdScenariosList:
            printRow = {"API": "0", "Well Name": "0", "Abandonment Date": "0",
                        "Gross Oil Well Head Volume": "0", "Gross Gas Well Head Volume": "0"}
        else:
            wellIdIndex = wellIdScenariosList.index(wellId)
            apiNumber = headerData[wellIdIndex]
            abandonmentDate = row["abandonmentDate"]
            grossOilWellHeadVolume = row["grossOilWellHeadVolume"]
            grossGasWellHeadVolume = row["grossGasWellHeadVolume"]

            printRow = {"API": apiNumber, "Abandonment Date": abandonmentDate,
                        "Gross Oil Well Head Volume": grossOilWellHeadVolume, "Gross Gas Well Head Volume": grossGasWellHeadVolume}

        eurData.loc[len(eurData)+1] = printRow

    return eurData