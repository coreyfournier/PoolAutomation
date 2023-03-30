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
    pumps:string[];
  }