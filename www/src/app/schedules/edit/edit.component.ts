import { Observable, Subscription } from 'rxjs';
import { Component, ChangeDetectorRef,Input, NgZone } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ScheduleInfo } from '../schedule';
import { DatePipe } from '@angular/common';
import { EventInfo, ScheduleChangeEvent } from '../../app.events';
import { FormBuilder, FormGroup, Validators,FormArray, FormControl } from '@angular/forms';
import { MatDateFormats, MAT_NATIVE_DATE_FORMATS, DateAdapter } from '@angular/material/core';

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

export class SaveResponse
{
  success:boolean = false;
  error:string = '';
}

export class ScheduleEditComponent {

  form = this.formBuilder.group({
    //... other form controls ...
    schedules: this.formBuilder.array([])
  });

  scheduleInfo:ScheduleInfo = {
    schedules:[],
    overrides:[]
  };

  get schedules():FormArray {
    return this.form.controls["schedules"] as FormArray;
  }

  private scheduleUrl = environment.apiUrl + 'schedule/schedules';  // URL to web api
  datepipe: DatePipe = new DatePipe(environment.locale);
  timeFormat:string = environment.timeFormat;

  constructor(private http: HttpClient, public zone: NgZone, private formBuilder: FormBuilder, private readonly adapter: DateAdapter<Date>) { 
    this.adapter.setLocale("en-EN");
  }     

  ngOnInit(): void {    
    this.getSchedules().subscribe(s=> 
    {
        this.scheduleInfo = s;
        s.schedules.forEach(sch=>{
          const scheduleForm = this.formBuilder.group({
            name:[sch.name, Validators.required],
            scheduleStart:[this.datepipe.transform(sch.scheduleStart, "HH:mm"), Validators.required],
            scheduleEnd:[this.datepipe.transform(sch.scheduleEnd, "HH:mm"), Validators.required],
            id:[sch.id, Validators.required]
          });

          this.schedules.push(scheduleForm);
        });        
      });   
  }

  getSchedules():Observable<ScheduleInfo>{
    return this.http.get<ScheduleInfo>(this.scheduleUrl);
  }

  onSubmit():void 
  {    
    console.log("Submitted form");

    this.http.post<SaveResponse>(this.scheduleUrl,this.scheduleInfo).subscribe(s=>{
      if(s.success)
        console.log("Saved!!!");
      else
        console.log(`Failed to save: ${s.error}`);
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
