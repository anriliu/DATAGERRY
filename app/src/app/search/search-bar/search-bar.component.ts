/*
* DATAGERRY - OpenSource Enterprise CMDB
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

import {
  Component,
  ElementRef, NgZone,
  OnDestroy,
  OnInit,
  QueryList, Renderer2,
  ViewChild,
  ViewChildren
} from '@angular/core';
import { SearchBarTag, SearchBarTagSettings } from './search-bar-tag/search-bar-tag';
import { TypeService } from '../../framework/services/type.service';
import { CmdbType } from '../../framework/models/cmdb-type';
import { Subscription } from 'rxjs';
import { SearchBarTagComponent } from './search-bar-tag/search-bar-tag.component';
import { ActivatedRoute, NavigationEnd, Route, Router } from '@angular/router';
import { FormControl, FormGroup } from '@angular/forms';
import { debounceTime } from 'rxjs/operators';
import { CategoryService } from '../../framework/services/category.service';
import { CmdbCategory } from '../../framework/models/cmdb-category';
import { SearchService } from '../search.service';

@Component({
  selector: 'cmdb-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.scss']
})
export class SearchBarComponent implements OnInit, OnDestroy {

  // Child components
  @ViewChild('tagInput', { static: false }) tagInput: ElementRef;
  @ViewChild('inputDropdown', { static: false }) inputDropdown: ElementRef;
  @ViewChildren(SearchBarTagComponent) searchBarTagComponents: QueryList<SearchBarTagComponent>;

  // Tags data
  public tags: SearchBarTag[] = [];

  // Form
  public searchBarForm: FormGroup;

  // Dropdown
  public possibleTextResults: number = 0;
  public possibleTypes: CmdbType[] = [];
  public possibleCategories: CmdbCategory[] = [];

  // Subscriptions
  private routeChangeSubscription: Subscription;
  private textRegexSubscription: Subscription;
  private typeRegexSubscription: Subscription;
  private inputControlSubscription: Subscription;

  constructor(private router: Router, private route: ActivatedRoute, private searchService: SearchService,
              private typeService: TypeService, private categoryService: CategoryService) {
    this.searchBarForm = new FormGroup({
      inputControl: new FormControl('')
    });
    this.textRegexSubscription = new Subscription();
    this.typeRegexSubscription = new Subscription();
    this.inputControlSubscription = new Subscription();
    /*this.routeChangeSubscription = this.router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        const searchQuery = this.route.snapshot.queryParams.query;
        if (searchQuery !== undefined) {
          this.tags = JSON.parse(searchQuery) as SearchBarTag[];
        } else {
          this.tags = [];
        }
      }
    });*/
  }

  public ngOnInit(): void {

    this.inputControl.valueChanges.pipe(debounceTime(300)).subscribe((changes: string) => {
      if (changes !== '') {
        /*this.textRegexSubscription = this.searchService.getEstimateValueResults(changes).subscribe((counter: number) => {
          this.possibleTextResults = counter;
        });*/
        this.typeRegexSubscription = this.typeService.getTypesBy(changes).subscribe((typeList: CmdbType[]) => {
          this.possibleTypes = typeList;
        });
        this.typeRegexSubscription = this.categoryService.getCategoriesBy(changes).subscribe((categoryList: CmdbCategory[]) => {
          this.possibleCategories = categoryList;
        });
      } else {
        this.possibleTextResults = 0;
        this.possibleTypes = [];
        this.possibleCategories = [];
      }

    });
  }

  public get inputControl(): FormControl {
    return this.searchBarForm.get('inputControl') as FormControl;
  }

  public addTag(searchForm: string, params?: any) {
    const searchTerm = this.inputControl.value;
    const tag = new SearchBarTag(searchTerm, searchForm);
    switch (searchForm) {
      case 'type':
        const typeIDs: number[] = [];
        for (const type of params) {
          typeIDs.push(type.public_id);
        }
        tag.settings = { types: typeIDs } as SearchBarTagSettings;
        break;
      default:
        break;
    }
    console.log(tag);
    console.log(params);
  }

  public updateTag(changes: SearchBarTag) {
    const index: number = this.tags.indexOf(changes);
    console.log(changes);
    if (index !== -1) {
      // If searchText was cleared
      if (changes.searchText === '' || changes.searchText === undefined) {
        this.removeTag(changes);
      } else {
        this.tags[index] = changes;
      }
    }
  }

  public removeTag(tag: SearchBarTag) {
    const index: number = this.tags.indexOf(tag);
    if (index !== -1) {
      this.tags.splice(index, 1);
    }
  }

  public clearAll() {
    this.tags = [];
  }

  public callSearch() {
    if (this.tags.length > 0) {
      this.router.navigate(['/search'], { queryParams: { query: JSON.stringify(this.tags) } });
    }
  }

  public ngOnDestroy(): void {
    this.routeChangeSubscription.unsubscribe();
    this.textRegexSubscription.unsubscribe();
    this.typeRegexSubscription.unsubscribe();
    this.inputControlSubscription.unsubscribe();
  }

}