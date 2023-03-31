import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { TemperatureComponent } from './temperature/temperature.component';
import { HttpClientModule } from '@angular/common/http';
import { SchedulesComponent } from './schedules/schedules.component';
import { VariableGroupsComponent } from './variable-groups/variable-groups.component';

@NgModule({
  declarations: [
    AppComponent,
    TemperatureComponent,
    SchedulesComponent,
    VariableGroupsComponent
  ],
  imports: [
    HttpClientModule,
    BrowserModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }