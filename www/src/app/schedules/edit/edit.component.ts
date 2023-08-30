import { Observable, Subscription } from 'rxjs';
import { Component, ChangeDetectorRef,Input, NgZone } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ScheduleInfo } from '../schedule';
import { DatePipe } from '@angular/common';
import { EventInfo, ScheduleChangeEvent } from '../../app.events';

@Component({
  selector: 'app-schedules-edit',
  templateUrl: './edit.component.html',
  styleUrls: ['../schedules.component.css']
})

export class ScheduleEditComponent {
  
  scheduleInfo:ScheduleInfo = {
    schedules:[],
    overrides:[]
  };

  private scheduleUrl = environment.apiUrl + 'schedule/schedules';  // URL to web api
  datepipe: DatePipe = new DatePipe('en-US');
  timeFormat:string = 'hh:mm a';

  constructor(private http: HttpClient, public zone: NgZone) { 

  }     

  ngOnInit(): void {
    this.getSchedules().subscribe(s=> this.scheduleInfo = s);
   
  }

  getSchedules():Observable<ScheduleInfo>{
    return this.http.get<ScheduleInfo>(this.scheduleUrl);
  }
}
