import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FinanceService } from './services/finance.service';
import {
  Chart,
  CategoryScale,
  ChartConfiguration,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  ChartType,
  ChartData,
  ChartOptions,
  ChartTypeRegistry
} from 'chart.js';

Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend
);

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  @ViewChild('stockChart') stockChart!: ElementRef<HTMLCanvasElement>;
  chart!: Chart;
  error: string | null = null;
  ticker: string = '';
  stockData: StockData | null = null;  // Use the interface and initialize as null
  revenueTrends: any;
  earningsInsights: any;
  marketNews: any;

  constructor(private financeService: FinanceService) { }

  ngOnInit() {
    this.fetchHistoricalTopStocks();
    this.fetchMarketNews();
    this.fetchRevenueTrends('AAPL');
    this.fetchEarningsInsights('AAPL');
  }

  changeChart(type: ChartType) {
    if (!this.stockData) {
      return; // Guard clause if there's no data
    }
    // Assume `stockData` holds data necessary for all chart types
    this.initChart(type, {
      labels: Object.keys(this.stockData), // Adjust accordingly
      datasets: [{
        data: Object.values(this.stockData), // Adjust accordingly
        label: "Stock Performance",
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }]
    });
  }

  initChart(type: keyof ChartTypeRegistry, data: ChartConfiguration['data']) {
    if (this.chart) {
      this.chart.destroy();
    }

    const context = this.stockChart.nativeElement.getContext('2d');
    if (!context) {
      console.error('Failed to get canvas context');
      return;
    }

    const config: ChartConfiguration = {
      type: type as keyof ChartTypeRegistry,
      data: data,
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: false
          }
        }
      }
    };

    this.chart = new Chart(context, config);
  }

  fetchHistoricalTopStocks() {
    this.financeService.getHistoricalTopStocks().subscribe({
      next: (response) => {
        const chartData = {
          labels: response.dates,
          datasets: Object.keys(response.data).map(stock => ({
            label: stock,
            data: response.data[stock],
            borderColor: this.getRandomColor(),
            fill: false,
            tension: 0.1
          }))
        };
        this.initChart('line', chartData);  // Specify 'line' directly here
      },
      error: (err) => {
        this.error = 'Failed to fetch historical stock data';
        console.error(err);
      }
    });
  }

  getRandomColor(): string {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

  searchTicker(ticker: string) {
    this.financeService.getStockPrice(ticker).subscribe({
      next: (data) => {
        console.log('Stock Data:', data); // Handle display of individual stock data
        this.error = null;
      },
      error: (err) => {
        this.error = "Failed to fetch data for ticker: " + ticker;
        console.error(err);
        this.stockData = null;
      }
    });
  }

  fetchMarketNews() {
    this.financeService.getMarketNews().subscribe({
      next: (news) => this.marketNews = news,
      error: (err) => this.handleError(err)
    });
  }

  fetchRevenueTrends(ticker: string) {
    if (!ticker) {
      console.error("Ticker is required");
      return;
    }
    this.financeService.getRevenueTrends(ticker).subscribe({
      next: (data) => this.revenueTrends = data,
      error: (err) => this.handleError(err)
    });
  }

  // Call this method with a valid ticker
  fetchEarningsInsights(ticker: string) {
    if (!ticker) {
      console.error("Ticker is required");
      return;
    }
    this.financeService.getEarningsInsights(ticker).subscribe({
      next: (data) => this.earningsInsights = data,
      error: (err) => this.handleError(err)
    });
  }

  handleError(error: any) {
    console.error('An error occurred:', error);
    this.error = 'Failed to load data. Please try again later.';
  }

  toggleTheme(): void {
    document.body.classList.toggle('is-light');
  }
}

interface StockData {
  closing_price: number;
  // Add other properties that you expect in the response
}
