import { Component, Input, ChangeDetectorRef ,NgZone  } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { Temperature } from './temperature';
import { TemperatureService } from './temperature.service';
import { AppComponent, EventInfo, TemperatureChangeEvent } from '../app.component';

@Component({
  selector: 'app-temperature',
  templateUrl: './temperature.component.html',
  styleUrls: ['./temperature.component.css']
})

export class TemperatureComponent {
  @Input() events!: Observable<EventInfo>;
  private eventsSubscription!: Subscription;

  constructor(private heroService: TemperatureService, public zone: NgZone) {

  }

  sensors: Temperature[] = [];

  getSensors(): void {
    this.heroService.getSensors()
        .subscribe(heroes => this.sensors = heroes);
  }
  
  ngOnInit(): void {
    this.getSensors();

    //Allow the sensor values to get reloaded
    this.eventsSubscription = this.events.subscribe((d) => {
      if(d.dataType == "TemperatureChangeEvent")
      {
        console.log("Reloading the temp chart");  
        var sensorCopy = this.sensors.map(x=> x);
        
        for(var i = 0; i< sensorCopy.length; i++)
        {
            var data:TemperatureChangeEvent = new TemperatureChangeEvent(d.dataParsed);
            if(sensorCopy[i].id == data.id)
            {
              
              console.log("Changing "+ data.id + " " + data.name + " from " + sensorCopy[i].temp + " to " + data.temp);
              sensorCopy[i].temp = data.temp;
            }
        }
        console.log("resetting array");

        this.zone.run(() => this.sensors = sensorCopy)
      }
    });  
  }
}