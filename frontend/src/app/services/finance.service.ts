import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FinanceService {

  constructor(private http: HttpClient) { }

  getStockPrice(ticker: string): Observable<any> {
    return this.http.get(`http://localhost:5000/stock/${ticker}`);
  }

  getMetrics(): Observable<any> {
    return this.http.get('http://localhost:5000/metrics', { responseType: 'text' });
  }

  getTopStocks(): Observable<StockData> {
    return this.http.get<StockData>(`http://localhost:5000/top-stocks`);
  }

}

export interface StockData {
  [key: string]: number;
}
