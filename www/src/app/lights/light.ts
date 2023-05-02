import { Scene } from "./scene";

export interface Light{
    name:string;
    displayName:string;
    lightScenes:Scene[];
}