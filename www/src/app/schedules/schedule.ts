export interface ScheduleInfo {
    schedules:Schedule[];
    overrides:Override[];
  }

  export interface Override{
    displayName:string;
    name: string;
  }

  export class Schedule {
    id: number = 0;
    name: string = '';
    isActive:boolean = false;
    isRunning:boolean = false;
    duration:number = 0;
    scheduleStart:Date = new Date();
    scheduleEnd:Date = new Date();
    endTime:Date = new Date();
    startTime:Date = new Date();
    pumps:Pump[] = [];    
  }

  export class Pump
  {
    id: number;
    name: string;
    //Current speed
    speedName:string;
    displayName:string;    

    speeds:Speed[] = [];

    constructor(jsonParsed:any){
      this.id = jsonParsed.id;
      this.name = jsonParsed.name;
      this.speedName = jsonParsed.speedName;
      this.displayName = jsonParsed.displayName;
    }
  }

  export class Speed{
    name:string = '';
    isActive:boolean = true;
  }