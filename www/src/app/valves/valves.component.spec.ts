import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ValvesComponent } from './valves.component';

describe('ValvesComponent', () => {
  let component: ValvesComponent;
  let fixture: ComponentFixture<ValvesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ValvesComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ValvesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
