import { Injectable } from '@angular/core';
import { Temperature } from './temperature';
//import { HEROES } from './mock-temperature';
import { Observable, of } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
//import { MessageService } from './message.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})

export class TemperatureService {
  private sensorUrl = environment.apiUrl + 'temperature/sensors';  // URL to web api
    constructor(
      private http: HttpClient
      ) { }

  /** Log a HeroService message with the MessageService */
  private log(message: string) {
    //this.messageService.add(`HeroService: ${message}`);
    console.log(message);
  }

    /**
   * Handle Http operation that failed.
   * Let the app continue.
   *
   * @param operation - name of the operation that failed
   * @param result - optional value to return as the observable result
   */
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {

      // TODO: send the error to remote logging infrastructure
      console.error(error); // log to console instead

      // TODO: better job of transforming error for user consumption
      this.log(`${operation} failed: ${error.message}`);

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }

  getSensors(): Observable<Temperature[]> {
    return this.http.get<Temperature[]>(this.sensorUrl)
    .pipe(
      catchError(this.handleError<Temperature[]>('getHeroes', []))
    );
  }
}

