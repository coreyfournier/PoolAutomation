import { Observable } from 'rxjs';
import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {VariableGroup} from './variableGroup'
import {Variable} from './variableGroup';
import { environment } from 'src/environments/environment';
declare var $:any;

@Component({
  selector: 'app-variable-groups',
  templateUrl: './variable-groups.component.html',
  styleUrls: ['./variable-groups.component.css']
})

export class VariableGroupsComponent {
  constructor(
    private http: HttpClient
    ) { } 
  
  variableGroups:VariableGroup[] = []

  private variableGroupUrl = environment.apiUrl + 'variable/UiVariables';  // URL to web api
  private changeVariableUrl = environment.apiUrl + "variable/change";

  ngOnInit(): void {
    this.getVariableGroups().subscribe(vg=> this.variableGroups = vg);
  }

  ngAfterContentChecked() {      
    this.setToggleButton();
  }

  setToggleButton():void{
    $.each($('[id^=variable-][type=checkbox]'), (index:number, element:any) => {
      //console.log(JSON.stringify(element));

        $(element).bootstrapToggle({
          on: 'On',
          off: 'Off'
      });
    });
  }

  getVariableGroups():Observable<VariableGroup[]>{
    return this.http.get<VariableGroup[]>(this.variableGroupUrl);
  }

  variableChanged(item: Variable, event:any): void {
    
    if(item.dataType == "bool")
      item.value = event.target.checked;
    else
      item.value = event.target.value
    
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
