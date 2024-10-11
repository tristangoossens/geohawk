import { AfterViewInit, Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import ImageService from './services/image.service';
import { NewRoundResponse } from '../models/NewRoundResponse';
import { MapService } from './services/map.service';
import { RoundResult } from '../models/RoundResult';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import Swal from 'sweetalert2';
import { GameStatus } from '../models/GameStatus';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  providers: [ImageService, MapService],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements AfterViewInit {
  currentImageUrl: string = '';
  currentGameStatus: GameStatus = GameStatus.LOADING;
  gameStatusEnum = GameStatus;

  round: NewRoundResponse | undefined;
  roundResult: RoundResult | null = null;

  constructor(private imageService: ImageService, public mapService: MapService, private modalService: NgbModal) {
    this.randomStreetView();
  }

  ngAfterViewInit(): void {
    this.mapService.initializeMap('map');
  }

  randomStreetView() {
    this.currentGameStatus = GameStatus.LOADING;
    this.roundResult = null;

    this.imageService.getRandomStreetviewImageUrl().then((response) => {
      this.currentImageUrl = response!.image_url;
      this.currentGameStatus = GameStatus.READY_TO_GUESS;
      this.round = response;
    });

    // Load a placeholder image for now
    // Timeout is used to simulate a network request
    // setTimeout(() => {
    //   this.currentImageUrl = 'https://via.placeholder.com/640x640';
    //   this.isLoaded = true;
    //   this.round = {
    //     image_url: 'https://via.placeholder.com/640x640',
    //     actual_location: {
    //       latitude: 0,
    //       longitude: 0,
    //     },
    //     model_prediction: {
    //       latitude: 0,
    //       longitude: 0,
    //     },
    //   };
    // }, 2000);
  }

  userHasGuessed(): boolean {
    return this.mapService.placedMarker !== null;
  }

  submitGuess() {
    if (this.round) {
      this.roundResult = this.mapService.submitGuess(this.round.actual_location, this.round.model_prediction);

      this.currentGameStatus = this.roundResult.win ? GameStatus.WINNER : GameStatus.LOSER;

      Swal.fire({
        title: this.roundResult.win ? 'Congratulations, you beat the model!' : 'Oh no, the model was closer!',
        text: 'Model distance: ' + this.roundResult.modelDistance + ' km\nYour distance: ' + this.roundResult.userDistance + ' km',
        icon: this.roundResult.win ? 'success' : 'error',
        confirmButtonText: 'OK',
      });
    }
  }

  closeModal() {
    this.modalService.dismissAll();
  }

  newRound() {
    // Reload the page
    window.location.reload();
  }
}
