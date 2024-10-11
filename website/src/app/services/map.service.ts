import { Injectable, model } from '@angular/core';
import * as L from 'leaflet';
import { NewRoundResponse } from '../../models/NewRoundResponse';
import { Geolocation } from '../../models/Geolocation';
import { RoundResult } from '../../models/RoundResult';

@Injectable({
    providedIn: 'root'
})
export class MapService {
    private map: any;
    private guessSubmitted: boolean = false;
    private customUserMarker: L.Icon = L.icon({
        iconUrl: '/assets/img/pin-user.png',
        iconSize:     [34, 41],
        iconAnchor:   [14, 41],
    });

    private customModelMarker: L.Icon = L.icon({
        iconUrl: '/assets/img/pin-model.png',
        iconSize:     [34, 41],
        iconAnchor:   [14, 41],
    });

    private destinationMarker: L.Icon = L.icon({
        iconUrl: '/assets/img/pin-destination.png',
        iconSize:     [34, 41],
        iconAnchor:   [14, 41],
    });

    public placedMarker: any;

    initializeMap(mapId: string): void {
        this.placedMarker = null;
        this.guessSubmitted = false;

        this.map = L.map(mapId, {
            center: [39.8283, -98.5795],
            zoom: 5
        });

        // Add a on-click event listener to the map
        this.map.on('click', (e: any) => {
            this.placeGuess([e.latlng.lat, e.latlng.lng]);
        });

        // Add the open street map tile for a world map
        const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            minZoom: 3,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        });
        tiles.addTo(this.map);
    }

    submitGuess(actual_location: Geolocation, model_prediction: Geolocation): RoundResult {
        this.guessSubmitted = true;

        // Calculate the distance between the user guess and the actual location
        const actual = L.latLng(actual_location.latitude, actual_location.longitude);
        const userGuess = L.latLng(this.placedMarker.getLatLng().lat, this.placedMarker.getLatLng().lng);
        const modelGuess = L.latLng(model_prediction.latitude, model_prediction.longitude);

        // Place destination marker
        this.placeMarker([actual_location.latitude, actual_location.longitude], this.destinationMarker);

        // Place model prediction marker
        this.placeMarker([model_prediction.latitude, model_prediction.longitude], this.customModelMarker);

        // Draw a dotted line between the two points
        const model_to_actual_line = L.polyline([[actual_location.latitude, actual_location.longitude],
            [model_prediction.latitude, model_prediction.longitude]], {color: 'black', dashArray: '5, 5'})
        model_to_actual_line.addTo(this.map);

        // Draw a dotted line between the user guess and the actual location
        const user_to_acutual_line = L.polyline([[actual_location.latitude, actual_location.longitude],
            [this.placedMarker.getLatLng().lat, this.placedMarker.getLatLng().lng]], {color: 'blue', dashArray: '5, 5'})

        user_to_acutual_line.addTo(this.map);

        // Calculate the distance between the model/user prediction and the actual location in kilometers (rounded to 2 decimal places)
        const modelDistance = Math.round(actual.distanceTo(modelGuess) / 1000 * 100) / 100;
        const userDistance = Math.round(actual.distanceTo(userGuess) / 1000 * 100) / 100;

        // Show the distance on the lines
        model_to_actual_line.bindTooltip(modelDistance + ' km (model)', {permanent: true, direction: 'center', className: 'distance-label'});
        user_to_acutual_line.bindTooltip(userDistance + ' km (you)', {permanent: true, direction: 'center', className: 'distance-label'});

        return {
            modelDistance,
            userDistance,
            win: userDistance < modelDistance
        };
    }

    placeGuess(coordinates: [number, number]): void {
        if(this.guessSubmitted) return;

        if (this.placedMarker === null) this.placedMarker = L.marker(coordinates, {icon: this.customUserMarker}).addTo(this.map);
        else this.placedMarker.setLatLng(coordinates);
    }

    placeMarker(coordinates: [number, number], icon: L.Icon): void {
        L.marker(coordinates, {icon: icon}).addTo(this.map);
    }
}