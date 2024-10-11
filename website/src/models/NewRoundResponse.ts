import { Geolocation } from "./Geolocation";

export interface NewRoundResponse {
    image_url: string;
    actual_location: Geolocation;
    model_prediction: Geolocation;
}