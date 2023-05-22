export class EventInfo{  
    dataType:string = "";
    dataParsed:any = "";
  
    constructor(payload:string)
    {
      this.dataParsed = JSON.parse(payload);
      this.dataType = this.dataParsed.dataType;
    }
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

  export class Pump
  {
    name:string;
    id:number;
    displayName:string;
    currentSpeed:string;

    constructor(jsonParsed:any){
        this.id = jsonParsed.id;
        this.name = jsonParsed.name;
        this.currentSpeed = jsonParsed.currentSpeed;
        this.displayName = jsonParsed.displayName;
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

  export class ScheduleChangeEvent{
    name:string;
    id:number;
    isActive:boolean;
    isRunning:boolean;
    duration:number;
    scheduleStart:Date;
    scheduleEnd:Date;

    constructor(jsonParsed:any){
        this.name = jsonParsed.name;
        this.id = jsonParsed.id;
        this.isActive = jsonParsed.isActive;
        this.isRunning = jsonParsed.isRunning;
        this.duration = jsonParsed.duration;
        this.scheduleStart = jsonParsed.scheduleStart;
        this.scheduleEnd = jsonParsed.scheduleEnd;
      }
  }