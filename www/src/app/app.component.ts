import { Component, NgZone } from '@angular/core';
import { Observable, Subscription, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: [
  ]
})

export class AppComponent {
  title = 'Pool Automation';
  
  
  constructor(private _zone: NgZone, private http: HttpClient) {   

  }
  
}