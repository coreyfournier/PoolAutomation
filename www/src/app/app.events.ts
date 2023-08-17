//import { Action } from 'rxjs/internal/scheduler/Action';
import { Schedule, Pump } from './schedules/schedule';

export class EventInfo{  
    dataType:string = "";
    data:any = "";
  
    constructor(payload:string)
    {
      let dataParsed = JSON.parse(payload);
      this.dataType = dataParsed.dataType;

      if(dataParsed.dataType == "TemperatureChangeEvent")
        this.data = dataParsed.data as TemperatureChangeEvent;
      else if(dataParsed.dataType == "ValveChangeEvent")
        this.data = dataParsed as ValveChangeEvent;
      else if(dataParsed.dataType == "PumpChangeEvent")
        this.data = dataParsed.data as PumpChangeEvent;
      else if(dataParsed.dataType == "LightChangeEvent")
        this.data = dataParsed.data as LightChangeEvent;
      else if(dataParsed.dataType == "VariableChangeEvent")
        this.data = dataParsed.data as VariableChangeEvent;
      else if(dataParsed.dataType == "ScheduleChangeEvent")
        this.data = dataParsed.data as ScheduleChangeEvent;
      else if(dataParsed.dataType == "OverrideChangeEvent")        
        this.data = dataParsed.data as OverrideChangeEvent;
      else //Some unknown type
        this.data = dataParsed.data
    }
  }

  export class OverrideChangeEvent
  {
    data : Action|null = null;
  }

  export class Action {
    name:string = "";
    displayName:string = "";
  }
  
  export class TemperatureChangeEvent
  {
    id:number;
    name:string;
    shortName:string;
    temp:number;
    unit:string;
  
    constructor(jsonParsed:any){
      this.id = jsonParsed.id;
      this.name = jsonParsed.name;
      this.shortName = jsonParsed.shortName;
      this.temp = jsonParsed.temp;
      this.unit = jsonParsed.unit;
    }
  }

  export class ValveChangeEvent{
    name:string;
    id:number;
    isOn:boolean;
    displayName:string;

    constructor(jsonParsed:any){
        this.id = jsonParsed.id;
        this.name = jsonParsed.name;
        this.isOn = jsonParsed.isOn;
        this.displayName = jsonParsed.displayName;
      }
  }

  export class PumpChangeEvent{
    newSpeed:string;
    oldSpeed:string;
    pump:Pump;

    constructor(jsonParsed:any){
        this.newSpeed = jsonParsed.newSpeed;
        this.oldSpeed = jsonParsed.oldSpeed;
        this.pump = new Pump(jsonParsed.pump)
      }
  }

  export class LightChangeEvent{
    constructor(jsonParsed:any){
        this.name = jsonParsed.name;
        this.displayName = jsonParsed.displayName;
      }

    name:string;
    displayName:string;
  }

  export class VariableChangeEvent{
    hasExpired:boolean;
    name:string;
    dataType:string;
    displayName:string;
    expires:Date;
    value:any;

    constructor(jsonParsed:any){
        this.name = jsonParsed.name;
        this.displayName = jsonParsed.displayName;
        this.hasExpired = jsonParsed.hasExpired;
        this.dataType = jsonParsed.dataType;
        this.expires = jsonParsed.expires;
        this.value = jsonParsed.value;
      }
  }

  export class ScheduleChangeEvent  {
    data:Schedule;

    constructor(jsonParsed:any){
      this.data = new Schedule();
        this.data.name = jsonParsed.name;
        this.data.id = jsonParsed.id;
        this.data.isActive = jsonParsed.isActive;
        this.data.isRunning = jsonParsed.isRunning;
        this.data.duration = jsonParsed.duration;
        this.data.scheduleStart = jsonParsed.scheduleStart;
        this.data.scheduleEnd = jsonParsed.scheduleEnd;
        this.data.pumps = jsonParsed.pumps;
      }
  }