import { Component, Input, ChangeDetectorRef ,NgZone, OnDestroy  } from '@angular/core';
import { Observable, Subscription, timer } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { Temperature } from './temperature';
import { TemperatureService } from './temperature.service';
import { EventInfo, TemperatureChangeEvent } from '../app.events';
import { TrendService } from '../trends/trend.service';
import { Trend } from '../trends/trend';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-temperature',
  templateUrl: './temperature.component.html',
  styleUrls: ['./temperature.component.css']
})

export class TemperatureComponent implements OnDestroy {
  @Input() events!: Observable<EventInfo>;
  private eventsSubscription!: Subscription;
  private trendsSubscription?: Subscription;

  constructor(private sensorService: TemperatureService, private trendService: TrendService, public zone: NgZone) {

  }

  sensors: Temperature[] = [];
  //Keyed by sensor id. Empty until the backend says it has a database to read from.
  trends: { [key: string]: Trend[] } = {};

  getSensors(): void {
    this.sensorService.getSensors()
        .subscribe(s => this.sensors = s);
  }

  trendsFor(sensorId: number): Trend[] {
    return this.trends[sensorId] ?? [];
  }

  /**
   * Trends come from the state log, which only gets a new row every few minutes. Polling on a
   * timer keeps them current without a query for every temperature change event.
   */
  private watchTrends(): void {
    this.trendsSubscription = timer(0, environment.trendRefreshMinutes * 60 * 1000)
      .pipe(switchMap(() => this.trendService.getTemperatureTrends()))
      .subscribe(response => this.zone.run(() => this.trends = response.trends));
  }

  ngOnInit(): void {
    this.getSensors();
    this.watchTrends();

    //Allow the sensor values to get reloaded
    this.eventsSubscription = this.events.subscribe((d) => {
      if(d.dataType == "TemperatureChangeEvent")
      {
        console.log("Reloading the temp chart");  
        var sensorCopy = this.sensors.map(x=> x);
        
        for(var i = 0; i< sensorCopy.length; i++)
        {            
            if(sensorCopy[i].id == d.data.id)
            {              
              console.log("Changing "+ d.data.id + " " + d.data.name + " from " + sensorCopy[i].temp + " to " + d.data.temp);
              sensorCopy[i].temp = d.data.temp;
            }
        }
        console.log("resetting array");

        this.zone.run(() => this.sensors = sensorCopy)
      }
    });  
  }

  ngOnDestroy(): void {
    this.trendsSubscription?.unsubscribe();
    this.eventsSubscription?.unsubscribe();
  }
}
