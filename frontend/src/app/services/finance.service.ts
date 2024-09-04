import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FinanceService {

  private baseUrl = 'http://localhost:5000'; // Base URL for API endpoints
  private apiUrlKey = 'apiUrl'; // Key to store the API URL in localStorage

  constructor(private http: HttpClient) {
    const storedApiUrl = localStorage.getItem(this.apiUrlKey);
    if (storedApiUrl) {
      this.baseUrl = storedApiUrl;
    }
  }

  getApiUrl(): string {
    return this.baseUrl;
  }

  setApiUrl(url: string): void {
    this.baseUrl = url;
    localStorage.setItem(this.apiUrlKey, url);
  }

  getStockPrice(ticker: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/stock/${ticker}`);
  }

  getPortfolio(): Observable<any> {
    return this.http.get(`${this.baseUrl}/portfolio`);
  }

  getBalance(username: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/balance/${username}`);
  }

  getTickerSuggestions(query: string): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseUrl}/ticker-suggestions/${query}`);
  }

  getStockInfo(ticker: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/stock-info/${ticker}`);
  }

  buyStock(ticker: string, shares: number, userId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/buy`, { ticker, shares, user_id: userId });
  }

  sellStock(ticker: string, shares: number, userId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/sell`, { ticker, shares, user_id: userId });
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
    return this.http.get(`${this.baseUrl}/market-news`);
  }

  login(username: string, password: string) {
    return this.http.post(`${this.baseUrl}/login`, { username, password });
  }
}

export interface StockData {
  [key: string]: number;
}
