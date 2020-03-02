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
import logging
from typing import List

from cmdb.search.params import SearchParam
from cmdb.search.query import Pipeline
from cmdb.search.query.builder import Builder

LOGGER = logging.getLogger(__name__)


class PipelineBuilder(Builder):
    """Pipeline query builder for database aggregation search"""

    def __init__(self, pipeline: Pipeline = None):
        """Init constructor
        Args:
            pipeline: preset a for defined pipeline
        """
        self._pipeline = pipeline or Pipeline([])

    def __len__(self) -> int:
        """Get the number of aggregate pipes inside the pipeline
        Returns (int): number of pipes
        """
        return len(self.pipeline)

    def clear(self):
        """Clear the pipeline"""
        self.pipeline = Pipeline([])

    @property
    def pipeline(self) -> Pipeline:
        return self._pipeline

    @pipeline.setter
    def pipeline(self, pipes: List[dict]):
        self._pipeline = Pipeline(pipes)

    def add_pipe(self, pipe: dict):
        """Add a pipe to the pipeline"""
        self.pipeline.append(pipe)

    def remove_pipe(self, pipe: dict):
        """Remove a pipe to the pipeline"""
        self.pipeline.remove(pipe)

    def build(self, params: List[SearchParam]) -> Pipeline:
        """Build a pipeline query out of frontend params"""
        # clear pipeline
        self.clear()

        # text builds
        text_params = [_ for _ in params if _.search_form == 'text']
        for param in text_params:
            regex = self.regex_('fields.value', param.search_text)
            self.add_pipe(self.match_(regex))

        # type builds
        type_params = [_ for _ in params if _.search_form == 'type']
        for param in type_params:
            if param.settings and len(param.settings.get('types', [])) > 0:
                type_id_in = self.in_('type_id', param.settings['types'])
                self.add_pipe(self.match_(type_id_in))

        # public builds
        id_params = [_ for _ in params if _.search_form == 'publicID']
        for param in id_params:
            self.add_pipe(self.match_({'public_id': int(param.search_text)}))

        return self.pipeline
