import { BrowserModule } from '@angular/platform-browser';
import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { FormsModule, ReactiveFormsModule  } from '@angular/forms';

import { AppComponent } from './app.component';
import { TemperatureComponent } from './temperature/temperature.component';
import { HttpClientModule } from '@angular/common/http';
import { SchedulesComponent } from './schedules/schedules.component';
import { VariableGroupsComponent } from './variable-groups/variable-groups.component';
import { LightsComponent } from './lights/lights.component';
import { PumpsComponent } from './pumps/pumps.component';
import { ValvesComponent } from './valves/valves.component';
import { StatsComponent } from './stats/stats.component';
import { NgApexchartsModule } from "ng-apexcharts";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

@NgModule({
  declarations: [
    AppComponent,
    TemperatureComponent,
    SchedulesComponent,
    VariableGroupsComponent,
    LightsComponent,
    PumpsComponent,
    ValvesComponent,
    StatsComponent
  ],
  imports: [
    HttpClientModule,
    BrowserModule,
    FormsModule,
    NgApexchartsModule,
    BrowserAnimationsModule,
    MatDatepickerModule,
    MatNativeDateModule,
    FormsModule,
    ReactiveFormsModule 
  ],
  schemas: [ CUSTOM_ELEMENTS_SCHEMA],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }