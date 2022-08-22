import {Component, OnDestroy, OnInit} from '@angular/core';
import {Plant} from "./plant";
import {PlantService} from "./plant.service";
import {Board} from "./board";
import {BoardService} from "./board.service";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  public plants: Plant[] = []
  public boards: Board[] = []

  private boardInterval: number = 0;

  constructor(private plantService: PlantService, private boardService: BoardService) {
  }

  public ngOnInit(): void {
    this.plantService.getPlants().subscribe(plants => this.plants = plants)
    this.getBoards();
  }

  public ngOnDestroy(): void {
    clearInterval(this.boardInterval)
  }

  public getBoards(): void {
    this.boardService.getBoards().subscribe(boards => this.boards = boards)
  }

  public addPlant(plant: Plant): void {
    this.plantService.addPlant(plant).subscribe(plant => this.plants.push(plant))
  }

  public updatePlant(plant: Plant): void {
    this.plantService.updatePlant(plant).subscribe()
  }

  public deletePlant(id: number): void {
    this.plantService.deletePlant(id).subscribe(_ => this.plants = this.plants.filter(p => p.id !== id))
  }
}
