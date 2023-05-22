import { Observable, Subscription } from 'rxjs';
import { Component, AfterViewInit, OnInit, ViewChild, Input  } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {
  ChartComponent,
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexTooltip,
  ApexTitleSubtitle
} from "ng-apexcharts";
import { DatePipe } from '@angular/common';
import {FormGroup, FormControl} from '@angular/forms';
import {MatDatepickerModule} from '@angular/material/datepicker';
import { EventInfo } from '../app.events';

declare var $:any;

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  title: ApexTitleSubtitle;
};

@Component({
  selector: 'app-stats',
  templateUrl: './stats.component.html',
  styleUrls: ['./stats.component.css']
})


export class StatsComponent {
  private eventsSubscription!: Subscription;
  @Input() events!: Observable<EventInfo>;
  datepipe: DatePipe = new DatePipe('en-US');
  @ViewChild("chart", { static: false }) chart!: ChartComponent;
  public chartOptions: Partial<ChartOptions> | any;
  private lastDate:Date = new Date();

  myGroup = new FormGroup({
    start : new FormControl(new Date(new Date()).toISOString().slice(0, -1))
  });

  constructor(private http: HttpClient) { 
    this.chartOptions = {
      chart: {
        width:'100%',
        height:200,
        id: 'temperature-chart',                
        type: 'line'
      },
      series: [],
      xaxis:{
          type:"category",
          tickAmount:'dataPoints',
          title:{text:""},
          categories:[]
      },
      title:{text:"Avg Temperature by Hour"}
    };
    
  }
  
  updateTemperatureChart(value:Date) : void{    
    this.lastDate = value;
    this.getChartData(this.chartOptions, value);
  } 

  ngOnInit(): void {
    this.getChartData(this.chartOptions, new Date());     

    this.eventsSubscription = this.events.subscribe((d) => {
      
      if(d.dataType == "TemperatureChangeEvent")
      {
        console.log("Reloading the temp chart");      
        this.getChartData(this.chartOptions, this.lastDate);
      }
    });           
  }

  getChartData(options:any, now:Date):Observable<any>{
    var statusUrl = environment.apiUrl + "data/tempStats?query=CreatedDate ge " +  this.datepipe.transform(now,"yyyy-MM-dd");
    const req = this.http.get<any>(statusUrl);

    req.subscribe(response=> {
      var list = [];
      for(var d=0;d < response.data.length; d++)
          list.push({name: response.data[d].name, data: response.data[d].data});
      
        options.xaxis.categories= response.hours;
        options.series = list;          
    });
    return req; 
  } 
}
