import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PoolChemistryComponent } from './poolChemistry.component';

describe('EnvironmentalComponent', () => {
  let component: PoolChemistryComponent;
  let fixture: ComponentFixture<PoolChemistryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PoolChemistryComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PoolChemistryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
