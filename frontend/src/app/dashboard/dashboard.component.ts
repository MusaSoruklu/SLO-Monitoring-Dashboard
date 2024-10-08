import { Component, ElementRef, ViewChild } from '@angular/core';
import { FinanceService } from '../services/finance.service';
import { Chart, ChartConfiguration, ChartType, ChartTypeRegistry } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent {
  isLoggedIn = false; // This should be updated based on your authentication logic
  stockData: StockData | null = null;  // Use the interface and initialize as null
  revenueTrends = {
    dates: ['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', '2024-05-01'],
    revenues: [150000, 155000, 160000, 162000, 165000]
  };
  earningsInsights = {
    EPS: ['2.50', '2.75', '3.00', '3.25', '3.50'],
    ProfitMargin: ['20%', '21%', '21.5%', '22%', '22.5%']
  };
  marketNews: any;
  error: string | null = null;
  @ViewChild('stockChart') stockChart!: ElementRef<HTMLCanvasElement>;
  @ViewChild('revenueChart') revenueChart!: ElementRef<HTMLCanvasElement>;
  @ViewChild('earningsChart') earningsChart!: ElementRef<HTMLCanvasElement>;
  chart!: Chart;

  constructor(private financeService: FinanceService) { }

  ngOnInit() {
    this.fetchHistoricalTopStocks();
    this.fetchMarketNews();
  }

  ngAfterViewInit() {
    this.initCharts();
  }

  initCharts(): void {
    this.initRevenueChart();
    this.initEarningsChart();
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
        responsive: false,
        scales: {
          y: {
            beginAtZero: false
          }
        }
      }
    };

    this.chart = new Chart(context, config);
  }

  initRevenueChart() {
    const context = this.revenueChart.nativeElement.getContext('2d');
    if (!context) {
      console.error('Failed to get canvas context for revenue chart');
      return;
    }
    const revenueChartData = {
      labels: this.revenueTrends.dates,
      datasets: [{
        label: 'Revenue',
        data: this.revenueTrends.revenues,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)'
      }]
    };
    new Chart(context, {
      type: 'line',
      data: revenueChartData,
      options: { scales: { y: { beginAtZero: true } } }
    });
  }

  initEarningsChart() {
    const context = this.earningsChart.nativeElement.getContext('2d');
    if (!context) {
      console.error('Failed to get canvas context for earnings chart');
      return;
    }
    const earningsChartData = {
      labels: this.revenueTrends.dates,
      datasets: [{
        label: 'EPS',
        data: this.earningsInsights.EPS,
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.5)'
      }]
    };
    new Chart(context, {
      type: 'bar',
      data: earningsChartData,
      options: { scales: { y: { beginAtZero: true } } }
    });
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
        this.initChart('line', chartData);
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

  fetchMarketNews() {
    this.financeService.getMarketNews().subscribe({
      next: (news) => this.marketNews = news,
      error: (err) => this.handleError(err)
    });
  }

  handleError(error: any) {
    console.error('An error occurred:', error);
    this.error = 'Failed to load data. Please try again later.';
  }

}

interface StockData {
  closing_price: number;
}