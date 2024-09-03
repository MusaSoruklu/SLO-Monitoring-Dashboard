import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './dashboard/dashboard.component';
import { StocksComponent } from './stocks/stocks.component';
import { PortfolioComponent } from './portfolio/portfolio.component';
import { TradeSharesComponent } from './trade-shares/trade-shares.component';
import { TeamSettingsComponent } from './team-settings/team-settings.component';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'stocks', component: StocksComponent },
  { path: 'portfolio', component: PortfolioComponent },
  { path: 'trade-shares', component: TradeSharesComponent },
  { path: 'team-settings', component: TeamSettingsComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
