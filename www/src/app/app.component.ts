import { Component, NgZone, OnInit } from '@angular/core';
import { Observable, Subscription, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: [
  ]
})

export class AppComponent implements OnInit {
  title = 'Pool Automation';
  //Build number of the backend, shown at the bottom of the page. It changes with every deploy.
  version = '';

  constructor(private _zone: NgZone, private http: HttpClient) {

  }

  ngOnInit(): void {
    this.http.get<{version:string}>(environment.apiUrl + 'version').subscribe({
      next: v => this.version = v.version,
      error: () => this.version = 'unknown'
    });
  }

}
