import { Component, OnInit } from '@angular/core';
import { FinanceService } from '../services/finance.service';

@Component({
  selector: 'app-portfolio',
  templateUrl: './portfolio.component.html',
  styleUrls: ['./portfolio.component.css']
})
export class PortfolioComponent implements OnInit {
  portfolio: any[] = [];
  totalInvestment = 0;
  totalValue = 0;
  totalProfit = 0;
  overallProfitPercent = 0;

  constructor(private financeService: FinanceService) {}

  ngOnInit(): void {
    this.fetchPortfolio();
  }

  fetchPortfolio(): void {
    this.financeService.getPortfolio().subscribe((data: any) => {
      this.portfolio = data;
      this.calculateTotals();
    }, error => {
      console.error('Failed to fetch portfolio data', error);
    });
  }

  calculateTotals(): void {
    this.totalInvestment = this.portfolio.reduce((acc, stock) => acc + stock.purchase_price * stock.shares, 0);
    this.totalValue = this.portfolio.reduce((acc, stock) => acc + stock.current_price * stock.shares, 0);
    this.totalProfit = this.totalValue - this.totalInvestment;
    this.overallProfitPercent = (this.totalProfit / this.totalInvestment) * 100;
  }
}
