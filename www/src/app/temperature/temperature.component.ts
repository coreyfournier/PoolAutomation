import { Component, Input, ChangeDetectorRef ,NgZone  } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { Temperature } from './temperature';
import { TemperatureService } from './temperature.service';
import { EventInfo, TemperatureChangeEvent } from '../app.events';

@Component({
  selector: 'app-temperature',
  templateUrl: './temperature.component.html',
  styleUrls: ['./temperature.component.css']
})

export class TemperatureComponent {
  @Input() events!: Observable<EventInfo>;
  private eventsSubscription!: Subscription;

  constructor(private sensorService: TemperatureService, public zone: NgZone) {

  }

  sensors: Temperature[] = [];

  getSensors(): void {
    this.sensorService.getSensors()
        .subscribe(s => this.sensors = s);
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
}