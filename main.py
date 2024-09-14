# main.py
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from controllers import router
from google.oauth2 import service_account
import aiomysql
import json

app = FastAPI(docs_url=None, redoc_url=None)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.update({
            'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            'X-Frame-Options': 'DENY',
            'X-Content-Type-Options': 'nosniff',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Referrer-Policy': 'no-referrer-when-downgrade',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
            'X-Permitted-Cross-Domain-Policies': 'none',
            'Expect-CT': "max-age=86400, enforce, report-uri='https://example.com/report'"
        })
        return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(router)
