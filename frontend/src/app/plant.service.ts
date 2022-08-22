import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Observable} from "rxjs";
import {Plant} from "./plant";

@Injectable({
  providedIn: 'root'
})
export class PlantService {
  private url = "http://127.0.0.1:5000/plants"


  constructor(private http: HttpClient) {
  }

  public getPlants(): Observable<Plant[]> {
    return this.http.get<Plant[]>(`${this.url}`)
  }

  public getPlant(plantId: number): Observable<Plant> {
    return this.http.get<Plant>(`${this.url}/${plantId}`)
  }

  public addPlant(plant: Plant): Observable<Plant> {
    return this.http.post<Plant>(`${this.url}`, plant)
  }

  public deletePlant(plantId: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${plantId}`)
  }

  public updatePlant(plant: Plant): Observable<{ success: boolean }> {
    return this.http.patch<{ success: boolean }>(`${this.url}/${plant.id}`, plant)
  }
}
