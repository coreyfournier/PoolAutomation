import { Component } from '@angular/core';
import { Temperature } from './temperature';
//import { HEROES } from '../mock-heroes';
import { TemperatureService } from './temperature.service';

@Component({
  selector: 'app-temperature',
  templateUrl: './temperature.component.html',
  styleUrls: ['./temperature.component.css']
})

export class TemperatureComponent {

  constructor(private heroService: TemperatureService) {

  }

  sensors: Temperature[] = [];

  getSensors(): void {
    this.heroService.getSensors()
        .subscribe(heroes => this.sensors = heroes);
  }
  
  ngOnInit(): void {
    this.getSensors();
  }
}