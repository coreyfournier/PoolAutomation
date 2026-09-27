import { Observable, Subscription } from 'rxjs';
import { Component, ChangeDetectorRef,Input, NgZone } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ScheduleInfo } from './schedule';
import { DatePipe } from '@angular/common';
import { EventInfo, ScheduleChangeEvent } from '../app.events';

@Component({
  selector: 'app-schedules',
  templateUrl: './schedules.component.html',
  styleUrls: ['./schedules.component.css']
})

export class SchedulesComponent {
  private eventsSubscription!: Subscription;
  @Input() events!: Observable<EventInfo>;
  editSchedules:boolean = false
  
  scheduleInfo:ScheduleInfo = {
    schedules:[],
    overrides:[],
    MIN_YEAR:0,
    MAX_YEAR:0
  };

  private scheduleUrl = environment.apiUrl + 'schedule/schedules';  // URL to web api
  datepipe: DatePipe = new DatePipe(environment.locale);
  timeFormat:string = environment.timeFormat;

  constructor(private http: HttpClient, public zone: NgZone) { 

  }     

  ngOnInit(): void {
    this.getSchedules().subscribe(s=> this.scheduleInfo = s);

    //Allow the sensor values to get reloaded
    this.eventsSubscription = this.events.subscribe((d) => {
      if(d.dataType == "ScheduleChangeEvent")
      {
        console.log("Schedule changed");  
        var scheduleCopy = this.scheduleInfo.schedules.map(x=> x);
        
        for(var i = 0; i< scheduleCopy.length; i++)
        {            
            if(scheduleCopy[i].id == d.data.id)
            {              
              console.log("Changing schedule "+ d.data.id + " " + d.data.name + " running to " + d.data.isRunning);
              //Only the state is taken from the event. The event knows nothing about the pump display
              //names, those are filled in by the schedules endpoint, and replacing the whole row loses them.
              scheduleCopy[i].isRunning = d.data.isRunning;
              scheduleCopy[i].isActive = d.data.isActive;
            }
        }

        this.zone.run(() => this.scheduleInfo.schedules = scheduleCopy);
      }
      else if(d.dataType == "OverrideChangeEvent")
      {
        var foundIndex = null;

        if(this.scheduleInfo.overrides != null)
        {          
          for(var i = 0; i< this.scheduleInfo.overrides.length; i++)
          {
            if(this.scheduleInfo.overrides[i].name == d.data.name)
              foundIndex = i;             
          }
        }

        if(!d.data.overrideSchedule && foundIndex != null)
          this.scheduleInfo.overrides.splice(foundIndex, 1);
        else if(d.data.overrideSchedule)
          this.scheduleInfo.overrides.push(d.data);

        var copy = this.scheduleInfo;

        this.zone.run(() => this.scheduleInfo = copy);
      }      
    });
  }

  getSchedules():Observable<ScheduleInfo>{
    return this.http.get<ScheduleInfo>(this.scheduleUrl);
  }

  showEditSchedules():void
  {
      this.editSchedules = true;
  }
}
