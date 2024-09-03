import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FinanceService {

  private baseUrl = 'http://localhost:5000'; // Base URL for API endpoints

  constructor(private http: HttpClient) { }

  getStockPrice(ticker: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/stock/${ticker}`);
  }

  getHistoricalTopStocks(): Observable<any> {
    return this.http.get(`${this.baseUrl}/top-stocks/historical`);
  }

  getMetrics(): Observable<any> {
    return this.http.get(`${this.baseUrl}/metrics`, { responseType: 'text' });
  }

  getTopStocks(): Observable<StockData> {
    return this.http.get<StockData>(`${this.baseUrl}/top-stocks`);
  }

  getRevenueTrends(ticker: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/revenue-trends/${ticker}`);
  }

  getEarningsInsights(ticker: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/earnings-insights/${ticker}`);
  }

  getMarketNews(): Observable<any> {
    return this.http.get(`http://localhost:5000/market-news`);
  }

  login(username: string, password: string) {
    return this.http.post('http://localhost:5000/login', { username, password });
  }
}

export interface StockData {
  [key: string]: number;
}
