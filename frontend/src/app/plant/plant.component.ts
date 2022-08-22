import {Component, EventEmitter, Input, Output} from '@angular/core';
import {Plant} from "../plant";
import {PlantService} from "../plant.service";

@Component({
  selector: 'app-plant',
  templateUrl: './plant.component.html',
  styleUrls: ['./plant.component.css']
})
export class PlantComponent {
  @Output() public saved = new EventEmitter<Plant>();
  @Output() public deleted = new EventEmitter<number>();
  @Input() public plant: Plant = {
    id: 0,
    image: '',
    name: '',
    optimal_humidity: 0,
    optimal_moisture: 0,
    optimal_temperature: 0,
  };
}
