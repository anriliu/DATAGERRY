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

import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { DocapiSettingsListComponent } from './docapi-settings-list/docapi-settings-list.component';
import { DocapiSettingsAddComponent } from './docapi-settings-add/docapi-settings-add.component';
import { DocapiSettingsEditComponent } from './docapi-settings-edit/docapi-settings-edit.component';

const routes: Routes = [
  {
    path: '',
    data: {
      breadcrumb: 'List'
    },
    component: DocapiSettingsListComponent
  },
  {
    path: 'add',
    data: {
      breadcrumb: 'Add'
    },
    component: DocapiSettingsAddComponent
  },
  {
    path: 'edit/:publicId',
    data: {
      breadcrumb: 'Edit'
    },
    component: DocapiSettingsEditComponent
  }
];

@NgModule({
  declarations: [],
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DocapiSettingsRoutingModule { }
