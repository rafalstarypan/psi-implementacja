import requests

class SourceService:

    @staticmethod
    def _get_auth_headers(context=None):
        if context is None:
            context = {}
        request = context.get("request")
        if request and request.META.get("HTTP_AUTHORIZATION"):
            return {"Authorization": request.META["HTTP_AUTHORIZATION"]}
        from django.conf import settings
        return {"Authorization": f"Bearer {settings.INTERNAL_SERVICE_TOKEN}"}


    @staticmethod
    def exists(source_type, source_id, context=None):
        url = SourceService._detail_url(source_type, source_id)
        headers = SourceService._get_auth_headers(context)
        response = requests.get(url, headers=headers, timeout=3)
        return response.status_code == 200

    @staticmethod
    def create(source_type, payload, context=None):
        url = SourceService._create_url(source_type)
        headers = SourceService._get_auth_headers(context)
        response = requests.post(url, json=payload, headers=headers, timeout=3)

        if response.status_code != 201:
            raise Exception("Source creation failed")

        return response.json()["id"]

    @staticmethod
    def _detail_url(source_type, source_id):
        if source_type == "person":
            return f"http://localhost:8000/api/parties/persons/{source_id}/"
        if source_type == "institution":
            return f"http://api/parties/institutions/{source_id}/"
        raise ValueError("Invalid source_type")
