import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { Scene } from './scene';
import { Light } from './light';

@Component({
  selector: 'app-lights',
  templateUrl: './lights.component.html',
  styleUrls: ['./lights.component.css']
})

export class LightsComponent {
  constructor(private http: HttpClient) { 

  } 
  //'/light/change?name='+name+'&sceneIndex=' + selectedValue
  //'/light/off?name=' + name,
  private lightUrl = environment.apiUrl + "light/get";
  private lightOffUrl = environment.apiUrl + "light/off";
  private lightSceneChangeUrl = environment.apiUrl + "light/change";

  lights:Light[] = []

  ngOnInit(): void {
    this.getLights().subscribe(l=> this.lights = l);
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
