import { Component, NgZone } from '@angular/core';
import { Observable, Subscription, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { EventInfo } from './app.events';

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
}