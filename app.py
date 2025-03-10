import os
import boto3
import uvicorn

from fastapi import FastAPI
from starlette.responses import Response
from starlette.responses import RedirectResponse
from src.stages.Prediction import PredictionPipeline

AWS_REGION = 'eu-north-1'

app = FastAPI()

def get_ssl_credentials():
    ssm = boto3.client('ssm', region_name=AWS_REGION)

    cert = ssm.get_parameter(Name='/cert', WithDecryption=True)['Parameter']['Value']
    key = ssm.get_parameter(Name='/key', WithDecryption=True)['Parameter']['Value']

    with open("/tmp/cert.pem", "w") as cert_file:
        cert_file.write(cert)

    with open("/tmp/key.pem", "w") as key_file:
        key_file.write(key)

    return "/tmp/cert.pem", "/tmp/key.pem"

@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


@app.get("/train")
async def training():
    try:
        os.system("python -B main.py")
        return Response("Training successful !!")
    except Exception as e:
        return Response(f"Error Occurred! {e}")


@app.post("/predict")
async def predict_route(text: str):
    try:
        obj = PredictionPipeline()
        result = obj.predict(text)
        return {"summary": result}
    except Exception as e:
        raise e


if __name__ == "__main__":
    cert_path, key_path = get_ssl_credentials()

    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080, 
        ssl_keyfile=key_path, 
        ssl_certfile=cert_path
    )
