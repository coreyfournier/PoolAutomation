import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LightsComponent } from './lights.component';

describe('LightsComponent', () => {
  let component: LightsComponent;
  let fixture: ComponentFixture<LightsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LightsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LightsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
