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