import { Component, Input } from '@angular/core';
import { Observable, Subscription } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { Scene } from './scene';
import { Light } from './light';
import { EventInfo, LightChangeEvent } from '../app.events';

@Component({
  selector: 'app-lights',
  templateUrl: './lights.component.html',
  styleUrls: ['./lights.component.css']
})

export class LightsComponent {
  private eventsSubscription!: Subscription;
  @Input() events!: Observable<EventInfo>;
  private lightUrl = environment.apiUrl + "light/get";
  private lightOffUrl = environment.apiUrl + "light/off";
  private lightSceneChangeUrl = environment.apiUrl + "light/change";
  lights:Light[] = []

  constructor(private http: HttpClient) { 

  }   
  

  ngOnInit(): void {
    this.getLights().subscribe(l=> this.lights = l);

    this.eventsSubscription = this.events.subscribe((d) => {
      if(d.dataType == "LightChangeEvent")
      {
        console.log(`Event=${d.dataType}`);
      }
    });
  }

  getLights():Observable<Light[]>{
      return this.http.get<Light[]>(this.lightUrl);
  }

  sceneChanged(light:Light, event:any):void{
    let index:number = event.target["selectedIndex"];

    if(index > 1)
    {
      var sceneIndex:number = index -1;

      console.log("Light:" + light.name + " Scene:" + light.lightScenes[sceneIndex].name + " changed");
      const req = this.http.get<Light>(this.lightSceneChangeUrl + "?name=" + light.name + "&sceneIndex=" + sceneIndex);

      req.subscribe();
    }
    else if(index == 1)
    {
      console.log("Light:" + light.name + " Scene: Off changed");

      const req = this.http.get<Light>(this.lightOffUrl + "?name=" + light.name);
      req.subscribe();
    }
  }
}
