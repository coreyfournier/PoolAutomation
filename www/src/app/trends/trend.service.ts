import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { TrendResponse, NO_TRENDS } from './trend';

@Injectable({
  providedIn: 'root'
})
export class TrendService {
  private temperatureUrl = environment.apiUrl + 'temperature/trends';
  private chemistryUrl = environment.apiUrl + 'poolChemistry/trends';

  constructor(private http: HttpClient) { }

  getTemperatureTrends(): Observable<TrendResponse> {
    return this.get(this.temperatureUrl);
  }

  getChemistryTrends(): Observable<TrendResponse> {
    return this.get(this.chemistryUrl);
  }

  /**
   * Trends are a nice to have. A backend without a database, or one that is too old to know
   * about trends at all, should never stop a panel from showing its reading.
   */
  private get(url: string): Observable<TrendResponse> {
    return this.http.get<TrendResponse>(url).pipe(
      catchError(error => {
        console.log(`Trends are not available from ${url}: ${error.message}`);
        return of(NO_TRENDS);
      })
    );
  }
}
