import { Observable, Subscription } from 'rxjs';
import { Component, ChangeDetectorRef,Input, NgZone } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ScheduleInfo } from '../schedule';
import { DatePipe } from '@angular/common';
import { EventInfo, ScheduleChangeEvent } from '../../app.events';
import { FormBuilder, FormGroup, Validators,FormArray, FormControl } from '@angular/forms';

@Component({
  selector: 'app-schedules-edit',
  templateUrl: './edit.component.html',
  styleUrls: ['../schedules.component.css']
})

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

  constructor(private http: HttpClient, public zone: NgZone, private formBuilder: FormBuilder) { 

  }     

  ngOnInit(): void {    
    this.getSchedules().subscribe(s=> 
    {
        this.scheduleInfo = s;
        s.schedules.forEach(sch=>{
          const scheduleForm = this.formBuilder.group({
            name:[sch.name, Validators.required],
            scheduleStart:[sch.scheduleStart, Validators.required],
            scheduleEnd:[sch.scheduleEnd, Validators.required],
            id:[sch.id, Validators.required]
          });

          //this.form.controls["schedules"].push();

          this.schedules.push(scheduleForm);
        });        
      });   
  }

  getSchedules():Observable<ScheduleInfo>{
    return this.http.get<ScheduleInfo>(this.scheduleUrl);
  }

  onSubmit() {    
    console.log("Submitted form");
  }

  addLesson():void  {
    // const lessonForm = this.formBuilder.group({
    //   title: ['', Validators.required],
    //   level: ['beginner', Validators.required]
    // });
    // this.schedules.push(lessonForm);
  }

  deleteLesson(lessonIndex: number):void {
    //this.lessons.removeAt(lessonIndex);
  }

}
