import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VariableGroupsComponent } from './variable-groups.component';

describe('VariableGroupsComponent', () => {
  let component: VariableGroupsComponent;
  let fixture: ComponentFixture<VariableGroupsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VariableGroupsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VariableGroupsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
