import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import csv
from PIL import Image

RADIUS_KM = 6378.1


class GeolocationPredictionService:
    def __init__(self, model_path: str):
        self._model = self._load_model(model_path)

    @property
    def model(self):
        """Returns the loaded Keras model."""
        return self._model

    def _degrees_to_radians(deg):
        pi_on_180 = 0.017453292519943295
        return deg * pi_on_180

    def _loss_haversine(self, observation, prediction):
        obv_rad = tf.map_fn(self._degrees_to_radians, observation)
        prev_rad = tf.map_fn(self._degrees_to_radians, prediction)

        dlon_dlat = obv_rad - prev_rad
        v = dlon_dlat / 2
        v = tf.sin(v)
        v = v**2

        a = v[:,1] + tf.cos(obv_rad[:,1]) * tf.cos(prev_rad[:,1]) * v[:,0]

        c = tf.sqrt(a)
        c = 2* tf.math.asin(c)
        c = c*RADIUS_KM
        final = tf.reduce_sum(c)

        #MAE with the haversine distance in KM
        final = final/tf.dtypes.cast(tf.shape(observation)[0], dtype= tf.float32)

        return final

    def _load_model(self, model_path: str):
        """Load an existing Keras model from an H5 file."""
        try:
            model = load_model(model_path, custom_objects={"loss_haversine": self._loss_haversine})
            print("Model loaded successfully.")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def _preprocess(self, image_path: str) -> np.ndarray:
        """Load an image, resize it to 320x320, and normalize pixel values."""
        try:
            image = Image.open(image_path)
            image = image.resize((320, 320))
            image = image.convert("RGB")
            image_array = np.array(image) / 255.0
            image_array = np.expand_dims(image_array, axis=0)
            return image_array
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            raise

    def predict(self, image_path: str):
        """Run the preprocessed image through the model and return the prediction values."""
        preprocessed_image = self._preprocess(image_path)
        predictions = self.model.predict(preprocessed_image)[0]
        return predictions