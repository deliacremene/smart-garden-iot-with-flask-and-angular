import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Board} from "./board";
import {SensorReading} from "./sensor-reading";
import {PumpState} from "./pump-state";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class BoardService {
  private url = "http://127.0.0.1:5000/boards"

  constructor(private http: HttpClient) {
  }

  public getBoards(): Observable<Board[]> {
    return this.http.get<Board[]>(`${this.url}`);
  }

  public getSensorData(boardId: number, latest: number = 1): Observable<SensorReading[]> {
    return this.http.get<SensorReading[]>(`${this.url}/${boardId}/sensor-data`, {params: {latest}});
  }

  public changePumpState(boardId: number, pump_state: "on" | "off"): Observable<PumpState> {
    return this.http.put<PumpState>(`${this.url}/${boardId}/pump-state`, {pump_state});
  }

  public getPumpState(boardId: number): Observable<PumpState> {
    return this.http.get<PumpState>(`${this.url}/${boardId}/pump-state`);
  }

  public setPlantId(boardId: number, plant_id: number) {
    return this.http.patch(`${this.url}/${boardId}/plant`, {plant_id});
  }
}
