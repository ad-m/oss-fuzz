# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
################################################################################
"""Unit tests for build_and_run_coverage."""
import json
import os
import sys
import unittest
from unittest import mock

from pyfakefs import fake_filesystem_unittest

FUNCTIONS_DIR = os.path.dirname(__file__)
sys.path.append(FUNCTIONS_DIR)
# pylint: disable=wrong-import-position

import build_and_run_coverage
import build_project
import test_utils

# pylint: disable=no-member


class TestRequestCoverageBuilds(fake_filesystem_unittest.TestCase):
  """Unit tests for sync."""

  def setUp(self):
    self.maxDiff = None  # pylint: disable=invalid-name
    self.setUpPyfakefs()
    self.patcher = mock.patch('build_lib.get_unique_build_step_image_id',
                              return_value='UNIQUE_ID')
    self.mock_function = self.patcher.start()

  @mock.patch('build_lib.get_signed_url', return_value='test_url')
  @mock.patch('build_lib.download_corpora_steps',
              return_value=[{
                  'url': 'test_download'
              }])
  @mock.patch('build_project.get_datetime_now',
              return_value=test_utils.FAKE_DATETIME)
  def test_get_coverage_build_steps(self, mock_url, mock_corpora_steps,
                                    mock_get_datetime_now):
    """Test for get_build_steps."""
    del mock_url, mock_corpora_steps, mock_get_datetime_now
    project_yaml_contents = (
        'language: c++\n'
        'sanitizers:\n'
        '  - address\n'
        'architectures:\n'
        '  - x86_64\n'
        'main_repo: https://github.com/google/oss-fuzz.git\n')
    self.fs.create_dir(test_utils.PROJECT_DIR)
    test_utils.create_project_data(test_utils.PROJECT, project_yaml_contents)

    expected_build_steps_file_path = test_utils.get_test_data_file_path(
        'expected_coverage_build_steps.json')
    self.fs.add_real_file(expected_build_steps_file_path)
    with open(expected_build_steps_file_path) as expected_build_steps_file:
      expected_coverage_build_steps = json.load(expected_build_steps_file)

    config = build_project.Config(upload=False)
    project_yaml, dockerfile = build_project.get_project_data(
        test_utils.PROJECT)
    build_steps = build_and_run_coverage.get_build_steps(
        test_utils.PROJECT, project_yaml, dockerfile, config)
    self.assertEqual(build_steps, expected_coverage_build_steps)


if __name__ == '__main__':
  unittest.main(exit=False)
