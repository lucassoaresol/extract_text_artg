import requests
import ssl


class UnsafeAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.options |= ssl.OP_LEGACY_SERVER_CONNECT
        kwargs["ssl_context"] = context
        super().init_poolmanager(*args, **kwargs)

    def build_response(self, req, resp):
        response = super().build_response(req, resp)
        return response
