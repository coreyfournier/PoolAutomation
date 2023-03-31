import { Observable } from 'rxjs';
import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {VariableGroup} from './variableGroup'

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

  ngOnInit(): void {
    this.getVariableGroups().subscribe(vg=> this.variableGroups = vg);
  }

  getVariableGroups():Observable<VariableGroup[]>{
    return this.http.get<VariableGroup[]>(this.variableGroupUrl);
  }
}
