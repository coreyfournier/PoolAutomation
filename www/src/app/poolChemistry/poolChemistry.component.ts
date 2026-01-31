import { Observable, Subscription } from 'rxjs';
import { Component, Input } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { PoolChemistry } from './environmental';
import { environment } from 'src/environments/environment';
import { EventInfo } from '../app.events';
import {
  ApexChart,
  ApexPlotOptions,
  ApexFill,
  ApexStroke,
  ApexNonAxisChartSeries
} from "ng-apexcharts";

export type GaugeChartOptions = {
  series: ApexNonAxisChartSeries;
  chart: ApexChart;
  plotOptions: ApexPlotOptions;
  fill: ApexFill;
  stroke: ApexStroke;
  labels: string[];
};

@Component({
  selector: 'app-poolchemistry',
  templateUrl: './poolChemistry.component.html',
  styleUrls: ['./poolChemistry.component.css']
})
export class PoolChemistryComponent {
  private eventsSubscription!: Subscription;
  @Input() events!: Observable<EventInfo>;

  private environmentalUrl = environment.apiUrl + "poolChemistry/sensor";

  chemistry?:PoolChemistry = undefined;

  // pH gauge: range 6.0 - 8.5, optimal 7.2 - 7.6
  phChartOptions: Partial<GaugeChartOptions> | any;
  // ORP gauge: range 400 - 900 mV, optimal 700 - 750
  orpChartOptions: Partial<GaugeChartOptions> | any;

  // Reference ranges
  readonly phMin = 6.0;
  readonly phMax = 8.5;
  readonly phOptimalMin = 7.2;
  readonly phOptimalMax = 7.6;

  readonly orpMin = 400;
  readonly orpMax = 900;
  readonly orpOptimalMin = 700;
  readonly orpOptimalMax = 750;

  constructor(private http: HttpClient) {
    this.phChartOptions = this.createGaugeOptions('pH', 0, this.phMin, this.phMax);
    this.orpChartOptions = this.createGaugeOptions('ORP', 0, this.orpMin, this.orpMax);
  }

  createGaugeOptions(label: string, value: number, min: number, max: number): GaugeChartOptions {
    const percentage = this.valueToPercentage(value, min, max);

    return {
      series: [percentage],
      chart: {
        type: 'radialBar',
        height: 180,
        background: 'transparent',
        fontFamily: "'Martian Mono', 'Courier New', monospace",
        sparkline: {
          enabled: false
        }
      },
      plotOptions: {
        radialBar: {
          startAngle: -135,
          endAngle: 135,
          hollow: {
            size: '65%',
            background: 'transparent'
          },
          track: {
            background: 'rgba(0, 206, 209, 0.1)',
            strokeWidth: '100%',
            margin: 0
          },
          dataLabels: {
            name: {
              show: true,
              fontSize: '10px',
              fontFamily: "'Martian Mono', monospace",
              fontWeight: 600,
              color: '#4A6572',
              offsetY: -10
            },
            value: {
              show: true,
              fontSize: '24px',
              fontFamily: "'Martian Mono', monospace",
              fontWeight: 300,
              color: '#00CED1',
              offsetY: 5,
              formatter: (val: number) => {
                if (label === 'pH') {
                  return this.percentageToValue(val, this.phMin, this.phMax).toFixed(1);
                } else {
                  return Math.round(this.percentageToValue(val, this.orpMin, this.orpMax)).toString();
                }
              }
            }
          }
        }
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: 'dark',
          type: 'horizontal',
          shadeIntensity: 0.5,
          gradientToColors: ['#20B2AA'],
          inverseColors: false,
          opacityFrom: 1,
          opacityTo: 1,
          stops: [0, 100]
        }
      },
      stroke: {
        lineCap: 'round'
      },
      labels: [label]
    };
  }

  valueToPercentage(value: number, min: number, max: number): number {
    if (value <= min) return 0;
    if (value >= max) return 100;
    return ((value - min) / (max - min)) * 100;
  }

  percentageToValue(percentage: number, min: number, max: number): number {
    return min + (percentage / 100) * (max - min);
  }

  getPhStatus(): string {
    if (!this.chemistry) return '';
    if (this.chemistry.ph >= this.phOptimalMin && this.chemistry.ph <= this.phOptimalMax) {
      return 'optimal';
    } else if (this.chemistry.ph < this.phOptimalMin - 0.3 || this.chemistry.ph > this.phOptimalMax + 0.3) {
      return 'warning';
    }
    return 'acceptable';
  }

  getOrpStatus(): string {
    if (!this.chemistry) return '';
    if (this.chemistry.orp >= this.orpOptimalMin && this.chemistry.orp <= this.orpOptimalMax) {
      return 'optimal';
    } else if (this.chemistry.orp < this.orpOptimalMin - 50) {
      return 'warning';
    }
    return 'acceptable';
  }

  updateGauges(): void {
    if (!this.chemistry) return;

    const phPercentage = this.valueToPercentage(this.chemistry.ph, this.phMin, this.phMax);
    const orpPercentage = this.valueToPercentage(this.chemistry.orp, this.orpMin, this.orpMax);

    // Update pH gauge color based on status
    const phColor = this.getPhStatus() === 'warning' ? '#FFD93D' :
                    this.getPhStatus() === 'optimal' ? '#20B2AA' : '#00CED1';

    // Update ORP gauge color based on status
    const orpColor = this.getOrpStatus() === 'warning' ? '#FFD93D' :
                     this.getOrpStatus() === 'optimal' ? '#20B2AA' : '#00CED1';

    this.phChartOptions = {
      ...this.phChartOptions,
      series: [phPercentage],
      fill: {
        ...this.phChartOptions.fill,
        gradient: {
          ...this.phChartOptions.fill.gradient,
          gradientToColors: [phColor]
        }
      }
    };

    this.orpChartOptions = {
      ...this.orpChartOptions,
      series: [orpPercentage],
      fill: {
        ...this.orpChartOptions.fill,
        gradient: {
          ...this.orpChartOptions.fill.gradient,
          gradientToColors: [orpColor]
        }
      }
    };
  }

  getData():Observable<PoolChemistry>
  {
    return this.http.get<PoolChemistry>(this.environmentalUrl);
  }

  ngOnInit(): void {
    this.getData().subscribe(p=> {
      this.chemistry = p;
      this.updateGauges();
    });

    this.eventsSubscription = this.events.subscribe((d) => {

      if(d.dataType == "OrpChangeEvent" || d.dataType == "PhChangeEvent")
      {
        console.log(`Event=${d.dataType}`);
        this.getData().subscribe(p=> {
          this.chemistry = p;
          this.updateGauges();
        });
      }
    });
  }
}
