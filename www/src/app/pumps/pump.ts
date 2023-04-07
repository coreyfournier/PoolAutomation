export interface Pump{
    id:number;
    name:string;
    displayName:string;
    currentSpeed:string;
    speeds:Speed[];
}

export interface Speed{
    name:string;
    isActive:boolean;
}