import { Component } from '@angular/core';
import { Observable, Subscription, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';

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
/*
<link rel="stylesheet" href="/css/bootstrap.min.css">
    <link rel="stylesheet" href="/css/site.css">
    <link rel="stylesheet" href="/css/bootstrap-toggle.min.css">
    <link rel="stylesheet" href="/apexcharts/apexcharts.css">
*/
export class AppComponent {
  title = 'Pool Automation';
  statInfo = "some data here";
  eventsSubject: Subject<void> = new Subject<void>();

  emitEventToChild() {
    
  }

  buttonClick() : void{
    
    this.eventsSubject.next();

    this.statInfo = "button clicked";
    console.log("Button CLicked");
  } 
}

