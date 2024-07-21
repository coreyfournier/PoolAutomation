export interface VariableGroup{
    title:string;
    variables:[Variable];
    isOnVariable:string;
    order:number;
}

export interface Variable{
    name:string;
    displayName:string;
    value:any;
    dataType:string;    
}