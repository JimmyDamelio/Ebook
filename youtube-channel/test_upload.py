"""Offline check of upload.py: python3 test_upload.py"""
import json
import os
import tempfile
import unittest
from unittest import mock

import upload


class Upload(unittest.TestCase):
    def setUp(self):
        self.calls = []

    def fake(self, url, data=None, headers=None, method=None):
        self.calls.append((url, data, headers or {}, method))
        if 'oauth2' in url:
            return {}, b'{"access_token": "tok"}'
        if 'uploadType=resumable' in url:
            return {'Location': 'https://upload.example/session'}, b''
        if url == 'https://upload.example/session':
            return {}, b'{"id": "abc", "status": {"privacyStatus": "public"}}'
        if '/channels?' in url:
            return {}, b'{"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "UU1"}}}]}'
        if '/playlistItems?' in url:
            return {}, json.dumps({'items': [{'snippet': {'title': 'T', 'description': 'Prompt: a boat\nmore'}}]}).encode()
        raise AssertionError(url)

    def test_upload_sends_metadata_then_file(self):
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            f.write(b'0123456789')
        with mock.patch.object(upload, 'call', self.fake):
            v = upload.upload('tok', f.name, {'title': 'x' * 150, 'description': 'd'})
        os.unlink(f.name)
        self.assertEqual(v['id'], 'abc')
        meta = json.loads(self.calls[0][1])
        self.assertEqual(len(meta['snippet']['title']), 100)
        self.assertEqual(self.calls[0][2]['X-Upload-Content-Length'], '10')
        self.assertEqual(self.calls[1][1:], (b'0123456789', {'Authorization': 'Bearer tok', 'Content-Type': 'video/mp4'}, 'PUT'))

    def test_past_uploads_reads_the_uploads_playlist(self):
        with mock.patch.object(upload, 'call', self.fake):
            self.assertEqual(upload.past_uploads('tok'), ['T | Prompt: a boat'])
        self.assertIn('playlistId=UU1', self.calls[1][0])

    def test_missing_secrets_exit_cleanly(self):
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaises(SystemExit) as e:
            upload.main(['list'])
        self.assertIn('YT_REFRESH_TOKEN', str(e.exception.code))


if __name__ == '__main__':
    unittest.main()
