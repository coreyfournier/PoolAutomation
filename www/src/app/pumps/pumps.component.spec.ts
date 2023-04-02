import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PumpsComponent } from './pumps.component';

describe('PumpsComponent', () => {
  let component: PumpsComponent;
  let fixture: ComponentFixture<PumpsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PumpsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PumpsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
