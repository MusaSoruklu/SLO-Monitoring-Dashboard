import { Component, OnInit } from '@angular/core';
import { FinanceService } from '../services/finance.service';

interface StockInfo {
  currentPrice: number;
  sharesOwned: number;
}

@Component({
  selector: 'app-trade-shares',
  templateUrl: './trade-shares.component.html',
  styleUrls: ['./trade-shares.component.css']
})
export class TradeSharesComponent implements OnInit {
  ticker: string = '';
  shares: number = 0;
  balance: number | null = null;
  tickerSuggestions: string[] = [];
  selectedTicker: string | null = null;
  currentStock: StockInfo | null = null;
  transactionInfo: string | null = null;

  constructor(private financeService: FinanceService) {}

  ngOnInit() {
    this.fetchBalance();
  }

  fetchBalance() {
    const username = sessionStorage.getItem('username');
    if (username) {
      this.financeService.getBalance(username).subscribe({
        next: (response: any) => this.balance = response.balance,
        error: (error) => console.error('Error fetching balance:', error)
      });
    }
  }

  searchTicker(query: string) {
    if (!query) return;
    this.financeService.getTickerSuggestions(query).subscribe({
      next: suggestions => this.tickerSuggestions = suggestions,
      error: () => this.tickerSuggestions = []
    });
  }

  loadStockInfo(ticker: string) {
    this.selectedTicker = ticker;
    this.financeService.getStockInfo(ticker).subscribe({
      next: stockInfo => this.currentStock = stockInfo,
      error: error => console.error('Error loading stock info:', error)
    });
  }

  buy() {
    if (this.selectedTicker && this.shares > 0) {
      this.financeService.buyStock(this.selectedTicker, this.shares, 'admin').subscribe({
        next: (response: any) => {
          this.transactionInfo = 'Purchase successful';
          this.loadStockInfo(this.selectedTicker!); // Reload stock info after purchase
          this.fetchBalance(); // Reload balance
        },
        error: (error) => this.transactionInfo = 'Purchase failed: ' + error.error.message
      });
    }
  }

  sell() {
    if (this.selectedTicker && this.shares > 0) {
      this.financeService.sellStock(this.selectedTicker, this.shares, 'admin').subscribe({
        next: (response: any) => {
          this.transactionInfo = 'Sale successful';
          this.loadStockInfo(this.selectedTicker!); // Reload stock info after sale
          this.fetchBalance(); // Reload balance
        },
        error: (error) => this.transactionInfo = 'Sale failed: ' + error.error.message
      });
    }
  }
}
