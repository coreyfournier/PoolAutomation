import { Observable, Subscription } from 'rxjs';
import { Component, AfterViewInit, OnInit, ViewChild, Input, NgZone  } from '@angular/core';
import { environment } from 'src/environments/environment';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {
  ChartComponent,
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexYAxis,
  ApexTooltip,
  ApexTitleSubtitle,
  ApexStroke,
  ApexGrid,
  ApexLegend,
  ApexMarkers
} from "ng-apexcharts";
import { DatePipe } from '@angular/common';
import {FormGroup, FormControl} from '@angular/forms';
import {MatDatepickerModule} from '@angular/material/datepicker';
import { EventInfo } from '../app.events';
import * as ApexCharts from 'apexcharts';

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  yaxis: ApexYAxis;
  title: ApexTitleSubtitle;
  stroke: ApexStroke;
  colors: string[];
  grid: ApexGrid;
  legend: ApexLegend;
  tooltip: ApexTooltip;
  markers: ApexMarkers;
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

  constructor(private http: HttpClient, public zone: NgZone) {
    this.chartOptions = this.getChart([], []);
  }

  getChart(categoryData:any, seriesData:any):any{
    return {
      chart: {
        type: 'line',
        height: 200,
        width: '100%',
        id: 'temperature-chart',
        background: 'transparent',
        fontFamily: "'Martian Mono', 'Courier New', monospace",
        toolbar: {
          show: false
        },
        zoom: {
          enabled: false
        },
        animations: {
          enabled: true,
          easing: 'easeinout',
          speed: 800,
          animateGradually: {
            enabled: true,
            delay: 150
          },
          dynamicAnimation: {
            enabled: true,
            speed: 350
          }
        }
      },
      series: seriesData,
      colors: ['#00CED1', '#F4A460', '#20B2AA', '#FFD93D'],
      stroke: {
        curve: 'smooth',
        width: 2
      },
      markers: {
        size: 0,
        hover: {
          size: 5
        }
      },
      xaxis: {
        categories: categoryData,
        tickAmount: 1,
        type: 'category',
        labels: {
          show: true,
          style: {
            colors: '#8BA9B3',
            fontSize: '10px',
            fontFamily: "'Martian Mono', monospace"
          }
        },
        axisBorder: {
          color: 'rgba(0, 206, 209, 0.15)'
        },
        axisTicks: {
          color: 'rgba(0, 206, 209, 0.15)'
        }
      },
      yaxis: {
        labels: {
          style: {
            colors: '#8BA9B3',
            fontSize: '10px',
            fontFamily: "'Martian Mono', monospace"
          },
          formatter: function(val: number) {
            return val + '°F';
          }
        }
      },
      grid: {
        borderColor: 'rgba(0, 206, 209, 0.1)',
        strokeDashArray: 3
      },
      legend: {
        position: 'top',
        horizontalAlign: 'right',
        floating: true,
        offsetY: -8,
        labels: {
          colors: '#8BA9B3'
        },
        markers: {
          width: 8,
          height: 8,
          radius: 2
        },
        itemMargin: {
          horizontal: 12
        }
      },
      tooltip: {
        theme: 'dark',
        x: {
          show: true
        },
        y: {
          formatter: function(val: number) {
            return val + '°F';
          }
        }
      },
      title: {
        text: 'Avg Temperature by Hour',
        align: 'left',
        style: {
          fontSize: '12px',
          fontWeight: 400,
          fontFamily: "'Young Serif', Georgia, serif",
          color: '#E8F4F8'
        }
      }
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
    var nowCopy = new Date(now.valueOf())
    var startDate = this.datepipe.transform(nowCopy, "yyyy-MM-dd");
    var endDate = this.datepipe.transform(nowCopy.setDate(nowCopy.getDate() + 1), "yyyy-MM-dd");
    var statusUrl = environment.apiUrl + "data/tempStats?query=CreatedDate ge " +  startDate + "T01:01:01 and CreatedDate lt " + endDate;
    const req = this.http.get<any>(statusUrl);

    req.subscribe(response=> {
      var list = [];

      for(var d=0;d < response.data.length; d++)
      {
          list.push({name: response.data[d].name, data: response.data[d].data});
      }

      options.series = list;

      ApexCharts.exec("temperature-chart", "updateOptions", {
        xaxis: {
          categories: response.hours
        }
      });
    });

    return req;
  }
}
