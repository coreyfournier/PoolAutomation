import { Observable } from 'rxjs';
import { Component, AfterViewInit, OnInit, ViewChild  } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {
  ChartComponent,
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexTitleSubtitle
} from "ng-apexcharts";

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
  @ViewChild("chart",{}) chart: ChartComponent;
  public chartOptions: Partial<ChartOptions>;
  
  constructor(private http: HttpClient) { 
    this.chartOptions = {
      series: [
        {
          name: "My-series",
          data: [10, 41, 35, 51, 49, 62, 69, 91, 148]
        }
      ],
      chart: {
        height: 350,
        type: "bar"
      },
      title: {
        text: "My First Angular Chart"
      },
      xaxis: {
        categories: ["Jan", "Feb",  "Mar",  "Apr",  "May",  "Jun",  "Jul",  "Aug", "Sep"]
      }
    };
  }

  ngOnInit(): void {
    //this.getValves().subscribe(p=> this.valves = p);
  }

  loadChart():void {
    /*
    var options = {
      chart: {
          width:'100%',
          height:200,
          id: 'temperature-chart',                
          type: 'line'
      },
      noData:{text:"Loading...."},
      series: [],
      xaxis:{
          type:"category",
          tickAmount:'dataPoints'
      }
  };
  var chart = new ApexCharts(document.getElementById("temperature-chart"), options);
   
  chart.render();
  
  const date = new Date($.now());

  $.getJSON("/data/tempStats?query=CreatedDate ge " +  $.format.date(date,"yyyy-MM-dd"), function(response) {
      chart.updateOptions({
          xaxis: {
              categories: response.hours,
                  title: {
                      text: 'Avg Temperature by Hour'
                  }
          }});                    
      
          var list = [];
          for(var d=0;d < response.data.length; d++)
              list.push({name: response.data[d].name, data: response.data[d].data});

          ApexCharts.exec("temperature-chart","updateOptions",{
              xaxis:{
                  categories: response.hours
              },
              series:  list                    
          });  
  });
*/
  }  
}
