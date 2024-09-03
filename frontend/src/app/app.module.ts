import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { DashboardComponent } from './dashboard/dashboard.component';
import { StocksComponent } from './stocks/stocks.component';
import { PortfolioComponent } from './portfolio/portfolio.component';
import { TradeSharesComponent } from './trade-shares/trade-shares.component';
import { TeamSettingsComponent } from './team-settings/team-settings.component';


@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    StocksComponent,
    PortfolioComponent,
    TradeSharesComponent,
    TeamSettingsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
