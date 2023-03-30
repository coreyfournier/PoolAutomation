export interface ScheduleInfo {
    schedules:Schedule[];
    overrides:string[];
  }

  export interface Schedule {
    id: number;
    name: string;
    isActive:boolean;
    isRunning:boolean;
    duration:number;
    scheduleStart:Date;
    scheduleEnd:Date;
    pumps:Pump[];
  }

  export interface Pump
  {
    id: number;
    name: string;
    speedName:string;
    displayName:string;
  }