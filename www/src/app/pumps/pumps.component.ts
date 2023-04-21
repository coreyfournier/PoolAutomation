import { Observable } from 'rxjs';
import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Pump, Speed } from './pump';
import { environment } from 'src/environments/environment';


@Component({
  selector: 'app-pumps',
  templateUrl: './pumps.component.html',
  styleUrls: ['./pumps.component.css']
})
export class PumpsComponent {
  constructor(
    private http: HttpClient
    ) { } 
    private pumpUrl = environment.apiUrl + "pump/descriptions";
    private pumpChangeUrl = environment.apiUrl + "pump/on?";

    pumps:Pump[] = [];

    ngOnInit(): void {
      this.getPumps().subscribe(p=> this.pumps = p);
    }

    getPumps():Observable<Pump[]>{
      return this.http.get<Pump[]>(this.pumpUrl);
    }

    speedChanged(pump:Pump, control:any):void{
      this.ChangeSpeed(pump, control);
    }
    
    ChangeSpeed(pump:Pump, event:any):Observable<Pump>{
      let index:number = event.target["selectedIndex"];

      const req = this.http.get<Pump>(this.pumpChangeUrl + "id=" + pump.id + "&speed=" + pump.speeds[index].name);

      req.subscribe();
      return req; 
    }
}
