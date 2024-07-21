import { Observable, Subscription } from 'rxjs';
import { Component, Input } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {VariableGroup} from './variableGroup'
import {Variable} from './variableGroup';
import { environment } from 'src/environments/environment';
import { EventInfo, VariableChangeEvent } from '../app.events';

@Component({
  selector: 'app-variable-groups',
  templateUrl: './variable-groups.component.html',
  styleUrls: ['./variable-groups.component.css']  
})

export class VariableGroupsComponent {
  private eventsSubscription!: Subscription;
  @Input() events!: Observable<EventInfo>;
  variableGroups:VariableGroup[] = []
  private variableGroupUrl = environment.apiUrl + 'variable/UiVariables';  // URL to web api
  private changeVariableUrl = environment.apiUrl + "variable/change";

  constructor(private http: HttpClient) { 

  }   

  ngOnInit(): void {
    this.getVariableGroups().subscribe((vg)=> {
      //Sort the list by how the server is telling you the order of them.
      this.variableGroups = vg.sort((l, r) => {
        if (l.order > r.order) return 1;  
        if (l.order < r.order) return -1;

        return 0;
      });
  });

    this.eventsSubscription = this.events.subscribe((d) => {
      if(d.dataType == "VariableChangeEvent")
      {
        console.log(`Variable event=${d.dataType}`);
      }
    });
  }

  ngAfterContentChecked() {      
    this.setToggleButton();
  }

  setToggleButton():void{
   
  }

  getVariableGroups():Observable<VariableGroup[]>{
    return this.http.get<VariableGroup[]>(this.variableGroupUrl);
  }

  variableChanged(item: Variable, event:any): void {
    console.log("Variable changed clicked");

    //If the data types are not correct, then
    if(item.dataType == "bool")
    {
      //Reverse the value due to the way the toggle works
      item.value = !item.value;
    }
    else if(item.dataType == "float")
      item.value = parseFloat(event.target.value);
    else if(item.dataType == "int")
      item.value = parseInt(event.target.value);
    else
      item.value = event.target.value;
    
    console.log("variable=" + item.name + " changed Value=" + item.value);
    this.changeVariable(item);
    console.log("variable=" + item.name + " after changed");    
  }

  changeVariable(item: Variable): Observable<Variable>{
    const req = this.http.post<Variable>(this.changeVariableUrl, item);

    req.subscribe();
    return req; 
  }
}
