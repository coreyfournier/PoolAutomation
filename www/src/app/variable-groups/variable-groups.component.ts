import { Observable } from 'rxjs';
import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {VariableGroup} from './variableGroup'
import {Variable} from './variableGroup'

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

  private variableGroupUrl = 'http://localhost:8080/variable/UiVariables';  // URL to web api
  private changeVariableUrl = "http://localhost:8080/variable/change";

  ngOnInit(): void {
    this.getVariableGroups().subscribe(vg=> this.variableGroups = vg);
  }

  getVariableGroups():Observable<VariableGroup[]>{
    return this.http.get<VariableGroup[]>(this.variableGroupUrl);
  }

  variableChanged(item: Variable): void {
    console.log("variable=" + item.name + " changed");
    this.changeVariable(item);
    console.log("variable=" + item.name + " after changed");    
  }

  changeVariable(item: Variable): Observable<Variable>{
    const req = this.http.post<Variable>(this.changeVariableUrl, item);

    req.subscribe();
    return req; 
  }
}
