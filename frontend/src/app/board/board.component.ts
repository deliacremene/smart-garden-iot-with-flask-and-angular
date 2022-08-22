import {Component, Input, OnDestroy, OnInit} from '@angular/core';
import {Board} from "../board";
import {Plant} from "../plant";
import {BoardService} from "../board.service";
import {SensorReading} from "../sensor-reading";

@Component({
  selector: 'app-board',
  templateUrl: './board.component.html',
  styleUrls: ['./board.component.css']
})
export class BoardComponent implements OnInit, OnDestroy {
  @Input() public plants: Plant[] = []
  @Input() public board: Board = {
    id: 0,
    ip: '',
    plant_id: 0,
    status: '',
  }
  public pumpState: boolean = false;
  public intervalId: number = 0;
  public data: any[] = [];

  constructor(private boardService: BoardService) {
  }

  public ngOnInit(): void {
    this.boardService.getSensorData(this.board.id, 10).subscribe(readings => this.plotData(readings));
    this.intervalId = setInterval(() => this.boardService.getSensorData(this.board.id, 10).subscribe(readings => this.plotData(readings)), 5000);
    this.boardService.getPumpState(this.board.id).subscribe(pumpState => {
      this.pumpState = pumpState.pump_state === "on"
      console.log(this.board.id, this.pumpState)
    })
  }

  public ngOnDestroy(): void {
    clearInterval(this.intervalId);
  }

  public plotData(readings: SensorReading[]): void {
    const times = readings.map(r => r.time);
    const moisture_plot = {
      x: times,
      y: readings.map(r => r.moisture),
      type: 'scatter',
      name: 'moisture'
    };
    const humidity_plot = {
      x: times,
      y: readings.map(r => r.humidity),
      type: 'scatter',
      name: 'humidity'
    };
    const temperature_plot = {
      x: times,
      y: readings.map(r => r.temperature),
      type: 'scatter',
      name: 'temperature'
    };
    this.data = [humidity_plot, temperature_plot, moisture_plot];
  }

  public setPlant(plant_id: number) {
    this.boardService.setPlantId(this.board.id, plant_id).subscribe();
  }

  public changePumpState(state: boolean) {
    this.boardService.changePumpState(this.board.id, state ? "on" : "off").subscribe();
  }
}
