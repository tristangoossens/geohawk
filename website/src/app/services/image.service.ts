// Barebones service
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { NewRoundResponse } from '../../models/NewRoundResponse';

@Injectable({
  providedIn: 'root'
})
export default class ImageService {
    constructor(private http: HttpClient) {}

    BASE_URL: string = 'http://localhost:8000';

    async getRandomStreetviewImageUrl(): Promise<NewRoundResponse | undefined> {
        const url = `${this.BASE_URL}/api/RandomImageWithPrediction`;
        return await this.http.get<NewRoundResponse>(url).toPromise();
    }
}