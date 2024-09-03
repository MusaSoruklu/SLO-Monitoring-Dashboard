import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TradeSharesComponent } from './trade-shares.component';

describe('TradeSharesComponent', () => {
  let component: TradeSharesComponent;
  let fixture: ComponentFixture<TradeSharesComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TradeSharesComponent]
    });
    fixture = TestBed.createComponent(TradeSharesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
