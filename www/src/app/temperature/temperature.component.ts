import { Component } from '@angular/core';
import { Temperature } from '../temperature';
//import { HEROES } from '../mock-heroes';
import { TemperatureService } from '../temperature.service';

@Component({
  selector: 'app-temperature',
  templateUrl: './temperature.component.html',
  styleUrls: ['./temperature.component.css']
})

export class TemperatureComponent {

  constructor(private heroService: TemperatureService) {

  }

  //heroes = HEROES;
  heroes: Temperature[] = [];

  selectedHero?: Temperature;

  getHeroes(): void {
    this.heroService.getHeroes()
        .subscribe(heroes => this.heroes = heroes);
  }
  
  ngOnInit(): void {
    this.getHeroes();
  }

  onSelect(hero: Temperature): void {
    this.selectedHero = hero;
  }
}


/*
Copyright Google LLC. All Rights Reserved.
Use of this source code is governed by an MIT-style license that
can be found in the LICENSE file at https://angular.io/license
*/