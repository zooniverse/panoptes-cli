import requests

class Panoptes:
    _default_headers = {
        'Accept': 'application/vnd.api+json; version=1',
    }
    _default_get_headers = {}
    _default_put_headers = {}
    _default_post_headers = {}
    _default_put_post_headers = {
        'Content-Type': 'application/vnd.api+json; version=1'
    }

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def _headers_for_get(self):
        headers = self._default_headers.copy()
        headers.update(self._default_get_headers)
        return headers

    def _headers_for_put(self):
        headers = self._default_headers.copy()
        headers.update(self._default_put_post_headers)
        headers.update(self._default_get_headers)
        return headers

    def _headers_for_post(self):
        headers = self._default_headers.copy()
        headers.update(self._default_headers)
        headers.update(self._default_put_post_headers)
        headers.update(self._default_get_headers)
        return headers

    def get(self, path, params={}, headers={}):
        _headers = self._headers_for_get().copy()
        _headers.update(headers)
        headers = _headers

        r = requests.get(self.endpoint + path, params=params,  headers=headers)
        return r.json()

    def get_project(self, project_id, slug=None, display_name=None):
        if project_id is None:
            project_id = ''

        params = {
            'slug': slug,
            'display_name': display_name,
        }

        return self.get('/projects/%s' % project_id, params=params)
