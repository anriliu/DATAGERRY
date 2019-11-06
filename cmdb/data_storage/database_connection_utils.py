# DATAGERRY - OpenSource Enterprise CMDB
# Copyright (C) 2019 NETHINKS GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import TypeVar
from pymongo.errors import ConnectionFailure as MongoConnectionFailure

CLIENT = TypeVar('CLIENT')


class ConnectionStatus:

    def __init__(self, status: bool, message: str = None):
        self._status: bool = status  # Connected = True, Disconnected = False
        self.message: str = message or 'No message given'

    def status(self):
        return self._status