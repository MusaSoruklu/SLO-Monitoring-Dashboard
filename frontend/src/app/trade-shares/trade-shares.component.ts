import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

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

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.fetchBalance();
  }

  fetchBalance() {
    const username = sessionStorage.getItem('username');
    if (username) {
      this.http.get(`http://localhost:5000/balance/${username}`).subscribe({
        next: (response: any) => this.balance = response.balance,
        error: (error) => console.error('Error fetching balance:', error)
      });
    }
  }

  searchTicker(query: string) {
    if (!query) return;
    // Fetch ticker suggestions
    this.http.get<string[]>(`http://localhost:5000/ticker-suggestions/${query}`).subscribe({
      next: suggestions => this.tickerSuggestions = suggestions,
      error: () => this.tickerSuggestions = []
    });
  }

  loadStockInfo(ticker: string) {
    this.selectedTicker = ticker;
    this.http.get<StockInfo>(`http://localhost:5000/stock-info/${ticker}`).subscribe({
      next: stockInfo => this.currentStock = stockInfo,
      error: error => console.error('Error loading stock info:', error)
    });
  }

  buy() {
    if (this.selectedTicker && this.shares > 0) {
      this.http.post('http://localhost:5000/buy', { ticker: this.selectedTicker, shares: this.shares, user_id: 'admin' })
        .subscribe({
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
      this.http.post('http://localhost:5000/sell', { ticker: this.selectedTicker, shares: this.shares, user_id: 'admin' })
        .subscribe({
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
