import { Observable } from 'rxjs';
import { Component, AfterViewInit, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {Valve} from './valve';
import { environment } from 'src/environments/environment';
declare var $:any;

@Component({
  selector: 'app-valves',
  templateUrl: './valves.component.html',
  styleUrls: ['./valves.component.css']
})

export class ValvesComponent implements OnInit {

  constructor(private http: HttpClient) { 

  } 
    private valveUrl = environment.apiUrl + "valve/get";
    private valveOffUrl = environment.apiUrl + "valve/off?";
    private valveOnUrl = environment.apiUrl + "valve/on?";

    valves:Valve[] = [];

    ngAfterContentChecked() {
      
      this.setToggleButton();
    }

    setToggleButton():void{     
    }

    ngOnInit(): void {
      this.getValves().subscribe(p=> this.valves = p);
    }

    getValves():Observable<Valve[]>{
      return this.http.get<Valve[]>(this.valveUrl);
    }
    
    valveChanged(valve:Valve, event:any):void{
      //Reverse the value due to the way the toggle works
      valve.isOn = !valve.isOn;
      this.toggleValve(valve, event)      
    }

    toggleValve(valve:Valve, event:any):Observable<Valve>{      
      const url = valve.isOn ? this.valveOnUrl : this.valveOffUrl;
      const req = this.http.get<Valve>(url + "id=" + valve.id);

      req.subscribe();
      return req; 
    }
}