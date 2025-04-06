import { Observable, Subscription } from 'rxjs';
import { Component, ChangeDetectorRef,Input, NgZone } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Pump, Schedule, ScheduleInfo } from '../schedule';
import { DatePipe } from '@angular/common';
import { EventInfo, ScheduleChangeEvent } from '../../app.events';
import { FormBuilder, FormGroup, Validators,FormArray, FormControl } from '@angular/forms';
import { MatDateFormats, MAT_NATIVE_DATE_FORMATS, DateAdapter } from '@angular/material/core';
import { SaveResponse } from '../SaveResponse';

export const GRI_DATE_FORMATS: MatDateFormats = {
  ...MAT_NATIVE_DATE_FORMATS,
  display: {
    ...MAT_NATIVE_DATE_FORMATS.display,
    dateInput: {
      hour12:true,
      minute:'numeric'
    } as Intl.DateTimeFormatOptions,
  }
}

@Component({
  selector: 'app-schedules-edit',
  templateUrl: './edit.component.html',
  styleUrls: ['../schedules.component.css'],
 
})
export class ScheduleEditComponent {

  scheduleForm: FormGroup = this.formBuilder.group(
    {
      schedules : this.formBuilder.array([])
    });

  pumpForm = this.formBuilder.group({
    pumps:this.formBuilder.array([])
  });

  scheduleInfo:ScheduleInfo = {
    schedules:[],
    overrides:[]
  };

  avaliablePumps:Pump[] = [];

  get schedules():FormArray {
    return this.scheduleForm.controls["schedules"] as FormArray;
  }


 getSpeedsForPump(pumpName:string)
 {
    var found = this.avaliablePumps.filter(x=>  x.name == pumpName);
    if(found.length > 0)
      return found[0].speeds;
    else
      return [];

 }



  schedulePumps(index:number, control:any):FormArray
  {
    return control.controls.pumps;
  }

  private scheduleUrl = environment.apiUrl + 'schedule/schedules';  // URL to web api
  private pumpUrl = environment.apiUrl + "pump/descriptions";
  datepipe: DatePipe = new DatePipe(environment.locale);
  timeFormat:string = environment.timeFormat;

  constructor(private http: HttpClient, public zone: NgZone, private formBuilder: FormBuilder, private readonly adapter: DateAdapter<Date>) { 
    this.adapter.setLocale("en-EN");
  }     

  ngOnInit(): void {    
    this.getPumps().subscribe(p=> {
      this.avaliablePumps = p;
    });
    
    this.getSchedules().subscribe(s=> 
    {
        this.scheduleInfo = s;

        this.scheduleForm = this.formBuilder.group({
          schedules : this.formBuilder.array(s.schedules.map(sch=>{

            return  this.formBuilder.group({
              name:[sch.name, Validators.required],
              startTime:[this.datepipe.transform(sch.startTime, "hh:mm"), Validators.required],
              endTime:[this.datepipe.transform(sch.endTime, "hh:mm"), Validators.required],
              id:[sch.id, Validators.required],
              pumps:this.formBuilder.array(sch.pumps.map(p=>{

                return this.formBuilder.group({
                  name:[p.name, Validators.required],
                  speedName:[p.speedName, Validators.required],
                  id:[p.id, Validators.required],
                  displayName:[p.displayName, Validators.required]
                })
              }))
            });
          }))

        });              
      });   
  }

  getPumps():Observable<Pump[]>{
    return this.http.get<Pump[]>(this.pumpUrl);
  }

  getSchedules():Observable<ScheduleInfo>{
    return this.http.get<ScheduleInfo>(this.scheduleUrl);
  }

  onSubmit():void 
  {    
    console.log("Submitted form");    

    const scheduleCopy = JSON.parse(JSON.stringify(this.scheduleForm?.value.schedules));
    scheduleCopy.forEach((schedule:any, index:number, array:any)=>{

      schedule.startTime = "0001-01-01T" + schedule.startTime;
      schedule.endTime = "9999-01-01T" + schedule.endTime;
    });

    this.http.post<SaveResponse>(this.scheduleUrl, scheduleCopy)
    .subscribe(s=>{
      if(s.success)
        console.log("Saved!!!");
      else
      {
        console.log(`Failed to save: ${s.error}`);
        alert(s.error);
      }
    });
  }

  addItem():void
  {
    let nextId = 0;
    this.scheduleInfo.schedules.forEach(element => {
      if(element.id > nextId)
        nextId = element.id;
    });

    nextId ++;

    const newItem = this.formBuilder.group({
        name:['', Validators.required],
        scheduleStart:['', Validators.required],
        scheduleEnd:['', Validators.required],
        id:[nextId, Validators.required]
      });

      this.schedules.push(newItem);
  }

  deleteLesson(lessonIndex: number):void {
    //this.lessons.removeAt(lessonIndex);
  }

}
