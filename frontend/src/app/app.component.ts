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
export class AppComponent implements OnInit {
  isLoggedIn = false; // This should be updated based on your authentication logic
  showLoginDialog = false;
  loginUsername: string = '';
  loginPassword: string = '';

  @ViewChild('usernameInput') usernameInput!: ElementRef;
  error: string | null = null;

  constructor(private financeService: FinanceService) { }

  ngOnInit() {
    this.checkLoginStatus();
    this.applyTheme();
  }

  handleError(error: any) {
    console.error('An error occurred:', error);
    this.error = 'Failed to load data. Please try again later.';
  }

  checkLoginStatus(): void {
    const storedUsername = sessionStorage.getItem('username');
    this.isLoggedIn = !!storedUsername;  // Coerce to boolean: true if username exists, false otherwise
    if (this.isLoggedIn) {
      this.loginUsername = storedUsername!;
    }
  }

  applyTheme(): void {
    const theme = sessionStorage.getItem('theme');
    if (theme) {
      document.body.className = theme; // Set class to body based on stored theme
    }
  }

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
        sessionStorage.setItem('username', this.loginUsername); // Store username in session storage
        this.isLoggedIn = true;
        this.closeLoginDialog();
      },
      error: (error) => {
        console.error('Login failed', error);
        this.isLoggedIn = false;
      }
    });
  }

  logout(): void {
    sessionStorage.removeItem('username'); // Remove the stored username
    this.isLoggedIn = false;
    console.log('User logged out.');
  }

  toggleTheme(): void {
    const currentTheme = document.body.className;
    const newTheme = currentTheme === 'is-dark' ? 'is-light' : 'is-dark';
    document.body.className = newTheme;
    sessionStorage.setItem('theme', newTheme); // Store new theme in session storage
  }
}