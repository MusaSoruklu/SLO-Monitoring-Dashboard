import { Component, OnInit, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { Chart, registerables } from 'chart.js';
import { FinanceService } from '../services/finance.service';

@Component({
  selector: 'app-stocks',
  templateUrl: './stocks.component.html',
  styleUrls: ['./stocks.component.css']
})
export class StocksComponent implements OnInit, AfterViewInit {
  @ViewChild('stockChart') stockChart?: ElementRef<HTMLCanvasElement>;
  chart: Chart | null = null;
  ticker: string = '';
  stockData: any;

  constructor(private financeService: FinanceService) {
    Chart.register(...registerables);
  }

  ngOnInit(): void {
  }

  ngAfterViewInit(): void {
    // This method will be called after the view (and the child views) are initialized
    if (this.stockChart) {
      this.plotChart(); // You might call plotChart here if it's appropriate
    }
  }

  fetchStockData() {
    this.financeService.getStockPrice(this.ticker).subscribe(data => {
      this.stockData = data;
      if (this.stockChart) { // Check if stockChart is defined
        this.plotChart();
      }
    }, error => {
      console.error('Failed to fetch stock data', error);
    });
  }

  plotChart() {
    if (!this.stockData || !this.stockData.history || !this.stockChart) {
      return; // Ensure all necessary data and elements are available
    }
  
    const context = this.stockChart.nativeElement.getContext('2d');
    if (!context) {
      console.error('Failed to get canvas context');
      return; // Exit the function if context is null
    }
  
    const data = {
      labels: this.stockData.history.dates,
      datasets: [{
        label: `${this.ticker} Stock Price`,
        data: this.stockData.history.prices,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    };
  
    if (this.chart) {
      this.chart.destroy();
    }
  
    this.chart = new Chart(context, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: false
          }
        }
      }
    });
  }  
}
