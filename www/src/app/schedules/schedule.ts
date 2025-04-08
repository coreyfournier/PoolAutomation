export interface ScheduleInfo {
    schedules:Schedule[];
    overrides:Override[];
    MIN_YEAR:number;
    MAX_YEAR:number;
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
    id: number = 0;
    name: string = '';
    //Current speed
    speedName:string = '';
    displayName:string = '';    

    speeds:Speed[] = [];
    constructor(){};

    static fromJson(jsonParsed:any): Pump
    {
      let t = new Pump();

      t.id = jsonParsed.id;
      t.name = jsonParsed.name;
      t.speedName = jsonParsed.speedName;
      t.displayName = jsonParsed.displayName;
      return t;
    }    
  }

  export class Speed{
    name:string = '';
    isActive:boolean = true;
  }