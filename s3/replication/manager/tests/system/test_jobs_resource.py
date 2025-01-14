#!/usr/bin/env python3

#
# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

import aiohttp
import pytest

from fixtures.jobs import fdmi_job  # noqa: F401;

# Global job id to perform validations across test cases.
global_valid_job_id = ""


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_case_name, expected_http_status",
    [('valid_job', 201),
     ('empty_job', 500)])
async def test_post_job(logger, test_config,
                        fdmi_job,  # noqa: F811;
                        test_case_name, expected_http_status):
    """Post job tests."""
    test_data = {'valid_job': fdmi_job, 'empty_job': {}}

    test_payload = test_data[test_case_name]

    async with aiohttp.ClientSession() as session:
        # Add job and attributes
        async with session.post(test_config['url'] + '/jobs',
                                json=test_payload) as response:

            logger.debug('HTTP Response: Status: {}'.format(response.status))
            if test_case_name == "valid_job":
                response_body = await response.json()
                logger.debug('HTTP Response: Body: {}'.format(response_body))

                global global_valid_job_id
                global_valid_job_id = response_body["job_id"]

            assert expected_http_status == response.status, \
                "ERROR : Received http status : " + str(response.status) + \
                "Expected http status :" + str(expected_http_status)

            logger.info(
                'POST successful: http status: {}'.format(response.status))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_case_name, expected_http_status",
    [('valid_job', 200),
     ('missing_job', 404)])
async def test_get_job(logger, test_config,
                       fdmi_job,  # noqa: F811;
                       test_case_name, expected_http_status):
    """GET specific job tests."""
    if test_case_name == "valid_job":
        global global_valid_job_id
        job_id = global_valid_job_id
    elif test_case_name == "missing_job":
        job_id = "invalid-job-id"
    else:
        assert False, "Invalid test case."

    async with aiohttp.ClientSession() as session:
        # Get Job details.
        async with session.get(
                test_config['url'] + '/jobs/' + job_id) as response:

            logger.debug('HTTP Response: Status: {}'.format(response.status))

            if test_case_name == 'valid_job':
                response_body = await response.json()
                logger.debug('HTTP Response Body: {}'.format(response_body))

            assert expected_http_status == response.status, \
                "ERROR : Received http status : " + str(response.status) + \
                "Expected http status :" + str(expected_http_status)

            logger.info(
                'GET job successful: http status: {}'.format(response.status))


@pytest.mark.asyncio
async def test_get_jobs(logger, test_config):
    """GET jobs list, expected entries added in post."""
    expected_http_status = 200
    expected_count = 1

    global global_valid_job_id
    job_id = global_valid_job_id

    async with aiohttp.ClientSession() as session:
        # Get jobs list.
        async with session.get(
                test_config['url'] + '/jobs') as response:

            logger.debug('HTTP Response: Status: {}'.format(response.status))

            jobs_list = await response.json()
            logger.debug('HTTP Response Body: {}'.format(jobs_list))

            assert expected_http_status == response.status, \
                "ERROR : Received http status : " + str(response.status) + \
                "Expected http status :" + str(expected_http_status)

            assert len(jobs_list) == expected_count, \
                "ERROR : Invalid expected jobs count." + \
                "Received {} jobs.\nExpected {} jobs".format(
                    len(jobs_list), expected_count)

            # Access the first job.
            job = next(iter(jobs_list.items()))[1]
            assert job_id == job["job_id"], \
                "ERROR : Expected job is missing. job_id = {}".format(
                    job_id
            )

            logger.info(
                'GET job successful: http status: {}'.format(response.status))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "test_case_name, expected_http_status",
    [('valid_job', 204),
     ('missing_job', 404)])
async def test_delete_job(logger, test_config,
                          fdmi_job,  # noqa: F811;
                          test_case_name, expected_http_status):
    """DELETE specific job tests."""
    if test_case_name == "valid_job":
        global global_valid_job_id
        job_id = global_valid_job_id
    elif test_case_name == "missing_job":
        job_id = "invalid-job-id"
    else:
        assert False, "Invalid test case."

    async with aiohttp.ClientSession() as session:
        # Delete Job.
        async with session.delete(
                test_config['url'] + '/jobs/' + job_id) as response:

            logger.debug('HTTP Response: Status: {}'.format(response.status))

            assert expected_http_status == response.status, \
                "ERROR : Received http status : " + str(response.status) + \
                "Expected http status :" + str(expected_http_status)

            logger.info(
                'DELETE job successful: http status: {}'.format(
                    response.status))


@pytest.mark.asyncio
async def test_get_jobs_count(logger, test_config):
    """GET jobs count to validate deleted entry."""
    expected_http_status = 200
    expected_count = 0

    async with aiohttp.ClientSession() as session:
        async with session.get(
                test_config['url'] + '/jobs', params="count") as response:

            logger.debug('HTTP Response: Status: {}'.format(response.status))

            response_body = await response.json()
            logger.debug('HTTP Response Body: {}'.format(response_body))
            received_count = int(response_body["count"])

            assert expected_http_status == response.status, \
                "ERROR : Received http status : " + str(response.status) + \
                "Expected http status :" + str(expected_http_status)

            assert received_count == expected_count, \
                "ERROR : Expected count mismatch." + \
                "Received count : {}\nExpected count : {}".format(
                    received_count, expected_count)

            logger.info(
                'GET job successful: http status: {}'.format(response.status))
