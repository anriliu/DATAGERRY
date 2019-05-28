/*
* dataGerry - OpenSource Enterprise CMDB
* Copyright (C) 2019 NETHINKS GmbH
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as
* published by the Free Software Foundation, either version 3 of the
* License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU Affero General Public License for more details.

* You should have received a copy of the GNU Affero General Public License
* along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { DataTableDirective } from 'angular-datatables';
import { Subject } from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { NgxSpinnerService } from 'ngx-spinner';
import { ApiCallService } from '../../../services/api-call.service';


@Component({
  selector: 'cmdb-results-search',
  templateUrl: './search-results.component.html',
  styleUrls: ['./search-results.component.scss']
})

export class SearchResultsComponent implements OnInit, OnDestroy {

  @ViewChild(DataTableDirective)
  public dtElement: DataTableDirective;

  public dtOptions: DataTables.Settings = {};
  public dtTrigger: Subject<any> = new Subject();
  public results = [];
  private url: any;

  constructor(private apiCallService: ApiCallService, private router: Router, private spinner: NgxSpinnerService,
              private route: ActivatedRoute) {

    this.route.queryParams.subscribe(qParams => {
      this.url = 'search/?value=' + qParams.value;
      this.callObjects();
    });
  }

  ngOnInit() {
    this.dtOptions = {
      ordering: true,
      order: [[1, 'asc']],
      language: {
        search: '',
        searchPlaceholder: 'Filter...'
      }
    };
  }

  private callObjects() {
    this.apiCallService.callGetRoute(this.url).subscribe(
      data => {
        this.spinner.show();
        setTimeout( () => {
          this.results = data as [];
          this.rerender();
          this.dtTrigger.next();
          this.spinner.hide();
        }, 100);
      });
  }

  ngOnDestroy(): void {
    // Do not forget to unsubscribe the event
    this.dtTrigger.unsubscribe();
  }

  public rerender(): void {
    if (typeof this.dtElement.dtInstance !== 'undefined') {
      this.dtElement.dtInstance.then((dtInstance: DataTables.Api) => {
        // Destroy the table first
        dtInstance.destroy();
      });
    }

  }

}
