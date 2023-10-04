import { Observable, Subscription } from 'rxjs';
import { Component, Input } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { PoolChemistry } from './environmental';
import { environment } from 'src/environments/environment';
import { EventInfo } from '../app.events';

@Component({
  selector: 'app-poolchemistry',
  templateUrl: './poolChemistry.component.html',
  styleUrls: ['./poolChemistry.component.css']
})
export class PoolChemistryComponent {
  private eventsSubscription!: Subscription;
  @Input() events!: Observable<EventInfo>;
  
  private environmentalUrl = environment.apiUrl + "poolChemistry/sensor";

  chemistry?:PoolChemistry = undefined;

  constructor(private http: HttpClient) { 

  } 

  getData():Observable<PoolChemistry>
  {
    return this.http.get<PoolChemistry>(this.environmentalUrl);
  }

  ngOnInit(): void {
    this.getData().subscribe(p=> this.chemistry = p);

    this.eventsSubscription = this.events.subscribe((d) => {

      if(d.dataType == "OrpChangeEvent" || d.dataType == "PhChangeEvent")
      {
        console.log(`Even=${d.dataType}`);
      }
    });
  }
}
