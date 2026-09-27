import { Observable, Subscription, timer } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { Component, Input, NgZone, OnDestroy } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { PoolChemistry } from './environmental';
import { environment } from 'src/environments/environment';
import { EventInfo } from '../app.events';
import { TrendService } from '../trends/trend.service';
import { Trend } from '../trends/trend';

@Component({
  selector: 'app-poolchemistry',
  templateUrl: './poolChemistry.component.html',
  styleUrls: ['./poolChemistry.component.css']
})
export class PoolChemistryComponent implements OnDestroy {
  private eventsSubscription!: Subscription;
  private trendsSubscription?: Subscription;
  @Input() events!: Observable<EventInfo>;
  
  private environmentalUrl = environment.apiUrl + "poolChemistry/sensor";

  chemistry?:PoolChemistry = undefined;
  //Keyed by the reading name, ph and orp. Empty until the backend says it has a database to read from.
  trends: { [key: string]: Trend[] } = {};

  constructor(private http: HttpClient, private trendService: TrendService, public zone: NgZone) { 

  } 

  getData():Observable<PoolChemistry>
  {
    return this.http.get<PoolChemistry>(this.environmentalUrl);
  }

  trendsFor(reading: string): Trend[] {
    return this.trends[reading] ?? [];
  }

  /**
   * Trends come from the state log, which only gets a new row every few minutes. Polling on a
   * timer keeps them current without a query for every reading that comes in.
   */
  private watchTrends(): void {
    this.trendsSubscription = timer(0, environment.trendRefreshMinutes * 60 * 1000)
      .pipe(switchMap(() => this.trendService.getChemistryTrends()))
      .subscribe(response => this.zone.run(() => this.trends = response.trends));
  }

  ngOnInit(): void {
    this.getData().subscribe(p=> this.chemistry = p);
    this.watchTrends();

    this.eventsSubscription = this.events.subscribe((d) => {

      if(d.dataType == "OrpChangeEvent" || d.dataType == "PhChangeEvent")
      {
        console.log(`Even=${d.dataType}`);
      }
    });
  }

  ngOnDestroy(): void {
    this.trendsSubscription?.unsubscribe();
    this.eventsSubscription?.unsubscribe();
  }
}
