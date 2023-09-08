import { Observable, Subscription } from 'rxjs';
import { Component, ChangeDetectorRef,Input, NgZone } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ScheduleInfo } from '../schedule';
import { DatePipe } from '@angular/common';
import { EventInfo, ScheduleChangeEvent } from '../../app.events';
import { FormBuilder, FormGroup, Validators,FormArray } from '@angular/forms';

@Component({
  selector: 'app-schedules-edit',
  templateUrl: './edit.component.html',
  styleUrls: ['../schedules.component.css']
})

export class ScheduleEditComponent {
  form = this.formBuilder.group({
    //... other form controls ...
    lessons: this.formBuilder.array([])
});

  scheduleInfo:ScheduleInfo = {
    schedules:[],
    overrides:[]
  };

  get lessons():FormArray {
    return this.form.controls["lessons"] as FormArray;
  }

  private scheduleUrl = environment.apiUrl + 'schedule/schedules';  // URL to web api
  datepipe: DatePipe = new DatePipe('en-US');
  timeFormat:string = 'hh:mm a';

  constructor(private http: HttpClient, public zone: NgZone, private formBuilder: FormBuilder) { 

  }     

  ngOnInit(): void {
    
    this.getSchedules().subscribe(s=> this.scheduleInfo = s);
   
  }

  getSchedules():Observable<ScheduleInfo>{
    return this.http.get<ScheduleInfo>(this.scheduleUrl);
  }

  onSubmit() {    
    console.log("Submitted form");
  }

  addLesson():void  {
    const lessonForm = this.formBuilder.group({
      title: ['', Validators.required],
      level: ['beginner', Validators.required]
    });
    this.lessons.push(lessonForm);
  }

  deleteLesson(lessonIndex: number):void {
    this.lessons.removeAt(lessonIndex);
  }

}
