import { Component, NgZone } from '@angular/core';
import { Observable, Subscription, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: [
    './app.component.css',
    '../../css/bootstrap.min.css',
    '../../css/site.css',
    '../../css/bootstrap-toggle.min.css'
  ]
})

export class AppComponent {
  title = 'Pool Automation';
  eventsSubject: Subject<EventInfo> = new Subject<EventInfo>();
  

  constructor(private _zone: NgZone, private http: HttpClient) {

    this.createEventSource().subscribe(
      (e: EventInfo) => {
        this.eventsSubject.next(e);
        console.log('Message received: ' + e);
      }
    );

  }

  getEventSource(url:string): EventSource{
    return new EventSource(url);
  }
  
  createEventSource(): Observable<EventInfo> {
    const eventSource = new EventSource(environment.apiUrl + 'data/getUpdate');

    return new Observable(observer => {
        eventSource.onmessage = event => {
          observer.next(new EventInfo(event.data));
      };
    });
 }

  buttonClick() : void{    
    //this.eventsSubject.next(new EventInfo("It's here"));
    console.log("Button CLicked");
  } 
}

export class EventInfo{  
  dataType:string = "";
  dataParsed:any = "";

  constructor(payload:string)
  {
    this.dataParsed = JSON.parse(payload);
    this.dataType = this.dataParsed.dataType;
  }
}

export class TemperatureChangeEvent
{
  id:number;
  name:string;
  shortName:string;
  temp:number;
  unit:string;

  constructor(jsonParsed:any){
    this.id = jsonParsed.id;
    this.name = jsonParsed.name;
    this.shortName = jsonParsed.shortName;
    this.temp = jsonParsed.temp;
    this.unit = jsonParsed.unit;
  }
}