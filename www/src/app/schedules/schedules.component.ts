import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ScheduleInfo } from './schedule';
import { Observable } from 'rxjs';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-schedules',
  templateUrl: './schedules.component.html',
  styleUrls: ['./schedules.component.css']
})
export class SchedulesComponent {
  scheduleInfo:ScheduleInfo = {
    schedules:[],
    overrides:[]
  };

  private scheduleUrl = 'http://localhost:8080/schedule/schedules';  // URL to web api
  datepipe: DatePipe = new DatePipe('en-US');
  timeFormat:string = 'hh:mm a';
  
  constructor(
    private http: HttpClient
    ) { }    

  ngOnInit(): void {
    this.getSchedules().subscribe(s=> this.scheduleInfo = s);
  }

  getSchedules():Observable<ScheduleInfo>{
    return this.http.get<ScheduleInfo>(this.scheduleUrl);
  }
}
