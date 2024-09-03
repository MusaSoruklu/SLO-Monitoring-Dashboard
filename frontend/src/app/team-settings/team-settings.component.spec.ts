import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TeamSettingsComponent } from './team-settings.component';

describe('TeamSettingsComponent', () => {
  let component: TeamSettingsComponent;
  let fixture: ComponentFixture<TeamSettingsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TeamSettingsComponent]
    });
    fixture = TestBed.createComponent(TeamSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
