import { Component, ElementRef, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { FinanceService } from './services/finance.service';
import {
  Chart,
  CategoryScale,
  ChartConfiguration,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  BarController,
  BarElement,
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
  BarController,
  BarElement,
  Title,
  Tooltip,
  Legend
);

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  isLoggedIn = false; // This should be updated based on your authentication logic
  showLoginDialog = false;
  loginUsername: string = '';
  loginPassword: string = '';

  @ViewChild('stockChart') stockChart!: ElementRef<HTMLCanvasElement>;
  @ViewChild('revenueChart') revenueChart!: ElementRef<HTMLCanvasElement>;
  @ViewChild('earningsChart') earningsChart!: ElementRef<HTMLCanvasElement>;

  @ViewChild('usernameInput') usernameInput!: ElementRef;
  chart!: Chart;
  error: string | null = null;
  ticker: string = '';
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

  constructor(private financeService: FinanceService) { }

  openLoginDialog(): void {
    this.showLoginDialog = true;
    setTimeout(() => {
      this.usernameInput.nativeElement.focus();
    }, 0);
  }

  closeLoginDialog(): void {
    this.showLoginDialog = false;
  }

  submitLogin(): void {
    this.financeService.login(this.loginUsername, this.loginPassword).subscribe({
      next: (response) => {
        console.log('Login successful', response);
        this.closeLoginDialog();
        this.isLoggedIn = true;
      },
      error: (error) => {
        console.error('Login failed', error);
        this.isLoggedIn = false;
      }
    });
  }  

  logout(): void {
    this.isLoggedIn = false;
    console.log('User logged out.');
    // Additional logout logic goes here
  }

  toggleTheme(): void {
    document.body.classList.toggle('is-light');
  }
}

interface StockData {
  closing_price: number;
}
