import { Component, OnInit } from '@angular/core';
import { FinanceService } from '../services/finance.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-team-settings',
  templateUrl: './team-settings.component.html',
  styleUrls: ['./team-settings.component.css']
})
export class TeamSettingsComponent implements OnInit {
  apiForm: FormGroup;

  constructor(private financeService: FinanceService) {
    this.apiForm = new FormGroup({
      apiUrl: new FormControl(this.financeService.getApiUrl(), [Validators.required, Validators.pattern('https?://.+')])
    });
  }

  ngOnInit(): void {}

  saveSettings() {
    if (this.apiForm.valid) {
      const newUrl = this.apiForm.get('apiUrl')?.value;
      this.financeService.setApiUrl(newUrl);
      alert('API URL updated successfully!');
    }
  }
}
