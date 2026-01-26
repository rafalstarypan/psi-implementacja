from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """Health check endpoint for load balancer and container orchestration."""
    health_status = {
        "status": "healthy",
        "database": "unknown",
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"error: {str(e)}"
        return JsonResponse(health_status, status=503)

    return JsonResponse(health_status)
