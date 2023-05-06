import { BrowserModule } from '@angular/platform-browser';
import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { TemperatureComponent } from './temperature/temperature.component';
import { HttpClientModule } from '@angular/common/http';
import { SchedulesComponent } from './schedules/schedules.component';
import { VariableGroupsComponent } from './variable-groups/variable-groups.component';
import { LightsComponent } from './lights/lights.component';
import { PumpsComponent } from './pumps/pumps.component';
import { ValvesComponent } from './valves/valves.component';
import { StatsComponent } from './stats/stats.component';

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
    FormsModule
  ],
  schemas: [ CUSTOM_ELEMENTS_SCHEMA],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }