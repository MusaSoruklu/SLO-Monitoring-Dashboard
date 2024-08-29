import { Component, OnInit } from '@angular/core';
import { FinanceService } from './services/finance.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'finance-dashboard';
  stockData: any;
  topStocks: any; // Adjust if you have a specific type defined
  error: string | null = null;
  ticker: string = '';

  constructor(private financeService: FinanceService) { }

  ngOnInit() {
    this.fetchTopStocks();
  }

  fetchTopStocks() {
    this.financeService.getTopStocks().subscribe({
      next: (data) => {
        this.topStocks = data;
      },
      error: () => {
        this.error = 'Failed to fetch top stocks';
      }
    });
  }

  getLastPrice(prices: any): number {
    const lastDate = Object.keys(prices).pop(); // gets the last key
    return prices[lastDate!]; // returns the price associated with the last date
  }

  searchTicker(ticker: string) {
    this.financeService.getStockPrice(ticker).subscribe({
      next: (data) => {
        this.stockData = data;
        this.error = null;
      },
      error: (error) => {
        this.error = "Failed to fetch data";
        this.stockData = null;
      }
    });
  }
}
