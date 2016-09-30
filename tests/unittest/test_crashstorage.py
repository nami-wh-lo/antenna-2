# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from freezegun import freeze_time


class TestCrashStorage:
    @freeze_time('2011-09-06 00:00:00', tz_offset=0)
    def test_flow(self, client, payload_generator):
        """Verify posting a crash gets to crash storage in the right shape"""
        boundary, data = payload_generator('socorrofake1_withuuid.raw')

        result = client.post(
            '/submit',
            headers={
                'Content-Type': 'multipart/form-data; boundary=' + boundary,
            },
            body=data
        )
        assert result.status_code == 200

        # NOTE(willkg): We do this goofy thing to get the
        # BreakpadSubmitterResource using internal Falcon API things. It's
        # entirely possible that this will break when we upgrade Falcon, but
        # there's no other way to get this without doing other crazier things
        # and possibly breaking the time/space continuum.
        bsr, method_map, params = client.app._router.find('/submit')

        # Now we've got the BreakpadSubmitterResource, so we can pull out the
        # crashstorage, verify there's only one crash in it and then verify the
        # contents of the crash.
        crashstorage = bsr.crashstorage
        assert len(crashstorage.crashes) == 1
        crash = crashstorage.crashes[0]
        assert (
            crash['raw_crash'] ==
            {
                'ProductName': 'Test',
                'Version': '1.0',
                'dump_checksums': {'upload_file_minidump': 'e19d5cd5af0378da05f63f891c7467af'},
                'submitted_timestamp': '2011-09-06T00:00:00+00:00',
                'timestamp': 1315267200.0,
                'type_tag': 'bp',
                'uuid': 'de1bb258-cbbf-4589-a673-34f802160918'
            }
        )
        assert (
            crash['dumps'] ==
            {
                'upload_file_minidump': b'abcd1234'
            }
        )
        assert crash['crash_id'] == 'de1bb258-cbbf-4589-a673-34f802160918'
