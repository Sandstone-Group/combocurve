import combocurve as combocurve
import os
from dotenv import load_dotenv
from combocurve_api_v1 import ServiceAccount

load_dotenv()

pecosCountryOperating = os.getenv("PECOS_WORKING_DATA_DIRECTORY")
sandstoneComboCurveApiKey = os.getenv("SANDSTONE_COMBOCURVE_API_KEY_PASS")
sandstoneComoboCurveServiceAccount = ServiceAccount.from_file(os.getenv("SANDSTONE_COMBOCURVE_API_SEC_CODE"))

data = combocurve.getLatestScenarioOneLiner(
    headerData=pecosCountryOperating,
    projectIdKey="65395df68da1897076cc396b",
    scenarioIdKey="65396a813ead87f1b494c7b7",
    serviceAccount=sandstoneComoboCurveServiceAccount,
    comboCurveApi=sandstoneComboCurveApiKey
)

