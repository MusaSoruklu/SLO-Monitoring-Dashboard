import { Component, OnInit, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { Chart, ChartConfiguration, ChartTypeRegistry, ChartData } from 'chart.js';
import { FinanceService } from '../services/finance.service';

@Component({
  selector: 'app-stocks',
  templateUrl: './stocks.component.html',
  styleUrls: ['./stocks.component.css']
})
export class StocksComponent implements OnInit, AfterViewInit {
  @ViewChild('stockChart') stockChart!: ElementRef<HTMLCanvasElement>;
  chart: Chart | null = null;
  ticker: string = '';
  stockData: any;
  currentPrice: number | null = null;
  changePercent: number | null = null;
  averageVolume: number | null = null;

  constructor(private financeService: FinanceService) { }

  ngOnInit(): void {
    this.initPlaceholderData();
  }


  initPlaceholderData() {
    this.currentPrice = 0; // Placeholder for current price
    this.changePercent = 0; // Placeholder for % change
    this.initPlaceholderChart();
  }

  ngAfterViewInit(): void {
    this.initPlaceholderChart();
  }

  initPlaceholderChart() {
    if (this.stockChart && this.stockChart.nativeElement) {
      this.initChart({
        labels: ['Waiting for data...'], // Placeholder label
        datasets: [{
          label: 'Stock Price',
          data: [0], // Placeholder data
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          tension: 0.1
        }]
      });
    }
  }

  initChart(data: ChartData<'line', (number | null)[], unknown>) {
    if (!this.stockChart?.nativeElement) {
      console.error('Canvas element not available.');
      return;
    }
    const context = this.stockChart.nativeElement.getContext('2d');
    if (context) {
      if (this.chart) {
        this.chart.destroy(); // Destroy existing chart if any
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
    } else {
      console.error('Failed to get canvas context');
    }
  }

  fetchStockData() {
    this.financeService.getStockPrice(this.ticker).subscribe({
      next: (data) => {
        this.stockData = data;
        this.currentPrice = data.current_price;
        this.changePercent = this.calculateChangePercent(data.history.prices);
        this.averageVolume = this.calculateAverageVolume(data.volume);
        this.updateChartWithData();
      },
      error: (error) => {
        console.error('Failed to fetch stock data', error);
      }
    });
  }

  calculateAverageVolume(volumes: number[]): number {
    return volumes.reduce((acc, curr) => acc + curr, 0) / volumes.length;
  }

  calculateChangePercent(prices: number[]): number | null {
    if (prices.length < 2) return null; // Need at least two prices to calculate % change
    const last = prices[prices.length - 1];
    const secondLast = prices[prices.length - 2];
    return ((last - secondLast) / secondLast) * 100;
  }

  updateChartWithData() {
    if (!this.stockData || !this.stockData.history) {
      return;
    }

    const updatedData: ChartData<'line', (number | null)[], unknown> = {
      labels: this.stockData.history.dates,
      datasets: [{
        label: `${this.ticker} Stock Price`,
        data: this.stockData.history.prices,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    };

    this.initChart(updatedData);
  }
}
