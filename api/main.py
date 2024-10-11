import uuid
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from keras.models import load_model
from keras.optimizers import Adam
from services.geolocation_prediction_service import GeolocationPredictionService
from services.image_scrape_service import ImageScrapeService
import csv
import random

# Directory where the images are stored
app_url = "http://localhost:8000/"
image_dir = "static/"

# Load the model
prediction_service = GeolocationPredictionService("models/geohawk_usa_cnn_v2.h5")
image_scraping_service = ImageScrapeService()

app = FastAPI()
app.mount(f"/{image_dir}", StaticFiles(directory="static"), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/RandomImageWithPrediction")
def getRandomStreetviewImageWithPrediction():
    # Get a random image from the scraper
    latitude, longitude, image = image_scraping_service.get_random_image()

    # Save the image to the static directory (CURRENT TIMESTAMP AS FILENAME)
    image_path = f"{image_dir}{uuid.uuid4()}.png"
    image.save(image_path)

    # Run the image through the model
    model_predictions = prediction_service.predict(image_path)
    print(model_predictions)

    # Return the image path
    return JSONResponse(content={
        "image_url": f"{app_url}{image_path}",
        "actual_location": {
            "latitude": latitude,
            "longitude": longitude
        },
        "model_prediction": {
            "latitude": float(model_predictions[0]),
            "longitude": float(model_predictions[1])
        }
    })