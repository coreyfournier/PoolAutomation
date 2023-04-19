import { Observable } from 'rxjs';
import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {Valve} from './valve';

@Component({
  selector: 'app-valves',
  templateUrl: './valves.component.html',
  styleUrls: ['./valves.component.css']
})

export class ValvesComponent {

  constructor(
    private http: HttpClient
    ) { } 
    private valveUrl = "http://localhost:8080/valve/get";
    private valveOffUrl = "http://localhost:8080/valve/off?";
    private valveOnUrl = "http://localhost:8080/valve/on?";

    valves:Valve[] = [];

    ngOnInit(): void {
      this.getValves().subscribe(p=> this.valves = p);
    }

    getValves():Observable<Valve[]>{
      return this.http.get<Valve[]>(this.valveUrl);
    }
    
    valveChanged(valve:Valve, event:any):void{
      this.toggleValve(valve, event)      
    }

    toggleValve(valve:Valve, event:any):Observable<Valve>{      
      const url = event.target.checked ? this.valveOnUrl : this.valveOffUrl;
      const req = this.http.get<Valve>(url + "id=" + valve.id);

      req.subscribe();
      return req; 
    }
}