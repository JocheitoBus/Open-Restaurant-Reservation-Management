"""
FastAPI application entry point.

Initializes and configures the FastAPI application with lifespan management,
routers, and middleware.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.api.v1.endpoints import reservations, tables
from app.core.config import settings
from app.db import init_db, close_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    
    Handles database initialization on startup and cleanup on shutdown.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        Control back to FastAPI after startup
    """
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"🔧 Environment: {settings.environment}")
    logger.info(f"📊 Database: {settings.database_url}")
    
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    try:
        await close_db()
        logger.info("✅ Database connection closed successfully")
    except Exception as e:
        logger.error(f"❌ Failed to close database connection: {e}", exc_info=True)


def get_custom_swagger_ui_html(
    *, openapi_url: str, title: str, oauth2_redirect_url: str | None = None
) -> str:
    """Get custom Swagger UI HTML with dark theme and light blue accents."""
    # Try to load from custom HTML file first
    app_dir = Path(__file__).parent
    html_file = app_dir / "swagger_ui_custom.html"
    
    # Fallback to inline HTML
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <title>{title}</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
        <style>
          html {{
            box-sizing: border-box;
            overflow-y: scroll;
          }}
          
          * {{
            box-sizing: inherit;
          }}
          
          body {{
            margin: 0;
            background: #1a1a1a;
            color: #1a1a1a;
            font-family: sans-serif;
          }}
          
          .swagger-ui {{
            background: #1a1a1a;
          }}
          
          .swagger-ui .topbar {{
            background-color: #0d47a1;
            border-bottom: 2px solid #5a8cc0;
          }}
          
          .swagger-ui .topbar h1 {{
            color: #ffffff;
          }}
          
          .topbar-search-container {{
            filter: brightness(1.2);
          }}
          
          .swagger-ui .info {{
            margin: 50px 0;
            color: #e0e0e0;
          }}
          
          .swagger-ui .info .title {{
            color: #5a8cc0;
            font-size: 36px;
          }}
          
          .swagger-ui .info .description {{
            color: #a0a0a0;
          }}
          
          .swagger-ui .scheme-container {{
            background: #252525;
            border: 2px solid #5a8cc0;
            border-radius: 4px;
            padding: 20px;
            margin: 20px 0;
          }}
          
          .swagger-ui .btn {{
            background: #0d47a1;
            border: 1px solid #5a8cc0;
            color: #ffffff;
            border-radius: 4px;
            padding: 8px 16px;
            transition: all 0.3s ease;
          }}
          
          .swagger-ui .btn:hover {{
            background: #1565c0;
            border-color: #90caf9;
            box-shadow: 0 0 8px rgba(90, 140, 192, 0.5);
          }}
          
          .swagger-ui .opblock {{
            background: #242424;
            border: 1px solid #444;
            border-radius: 4px;
            margin: 10px 0;
          }}
          
          .swagger-ui .opblock:hover {{
            border-color: #5a8cc0;
          }}
          
          .swagger-ui .opblock.opblock-get {{
            background: rgba(13, 71, 161, 0.08);
            border-color: #5a8cc0;
          }}
          
          .swagger-ui .opblock.opblock-post {{
            background: rgba(56, 142, 60, 0.08);
            border-color: #5a8cc0;
          }}
          
          .swagger-ui .opblock.opblock-put {{
            background: rgba(245, 127, 23, 0.08);
            border-color: #5a8cc0;
          }}
          
          .swagger-ui .opblock.opblock-delete {{
            background: rgba(211, 47, 47, 0.08);
            border-color: #5a8cc0;
          }}
          
          .swagger-ui .opblock.opblock-patch {{
            background: rgba(123, 31, 162, 0.08);
            border-color: #5a8cc0;
          }}
          
          .swagger-ui .opblock-summary {{
            color: #e0e0e0;
            border-bottom: 1px solid #5a8cc0;
          }}
          
          .swagger-ui .opblock-summary-method {{
            background: #0d47a1;
            color: #ffffff;
            border-radius: 3px;
            padding: 4px 8px;
          }}
          
          .swagger-ui input[type="text"],
          .swagger-ui input[type="password"],
          .swagger-ui input[type="email"],
          .swagger-ui input[type="number"],
          .swagger-ui textarea,
          .swagger-ui select {{
            background: #333333;
            border: 1px solid #5a8cc0;
            color: #e0e0e0;
            border-radius: 4px;
            padding: 8px 12px;
            transition: all 0.2s ease;
          }}
          
          .swagger-ui input[type="text"]:focus,
          .swagger-ui input[type="password"]:focus,
          .swagger-ui input[type="email"]:focus,
          .swagger-ui input[type="number"]:focus,
          .swagger-ui textarea:focus,
          .swagger-ui select:focus {{
            background: #3a3a3a;
            border-color: #90caf9;
            box-shadow: 0 0 0 3px rgba(90, 140, 192, 0.2);
            outline: none;
          }}
          
          .swagger-ui .model-box {{
            background: #252525;
            border: 1px solid #5a8cc0;
            border-radius: 4px;
          }}
          
          .swagger-ui .response {{
            margin: 10px 0;
          }}
          
          .swagger-ui .response-col_status {{
            color: #e0e0e0;
          }}
          
          .swagger-ui .response-col {{
            color: #e0e0e0;
          }}
          
          .swagger-ui code {{
            background: #2a2a2a;
            color: #90caf9;
            border-radius: 3px;
            padding: 2px 6px;
            font-family: monospace;
          }}
          
          .swagger-ui pre {{
            background: #2a2a2a;
            border: 1px solid #5a8cc0;
            color: #90caf9;
            border-radius: 4px;
            padding: 12px;
            overflow-x: auto;
          }}
          
          .swagger-ui a {{
            color: #5a8cc0;
            text-decoration: none;
          }}
          
          .swagger-ui a:hover {{
            color: #90caf9;
            text-decoration: underline;
          }}
          
          .swagger-ui .markdown p,
          .swagger-ui .markdown h1,
          .swagger-ui .markdown h2,
          .swagger-ui .markdown h3,
          .swagger-ui .markdown h4,
          .swagger-ui .markdown h5,
          .swagger-ui .markdown h6 {{
            color: #e0e0e0;
          }}
          
          .swagger-ui .model {{
            color: #e0e0e0;
          }}
          
          .swagger-ui .model-title {{
            color: #5a8cc0;
          }}
          
          .swagger-ui .loading-container {{
            color: #5a8cc0;
          }}
          
          .swagger-ui .parameter__name {{
            color: #90caf9;
          }}
          
          .swagger-ui table {{
            background: #252525;
            border: 1px solid #5a8cc0;
          }}
          
          .swagger-ui table thead {{
            background: #0d47a1;
            color: #ffffff;
          }}
          
          .swagger-ui table tbody tr {{
            border-bottom: 1px solid #444;
            color: #e0e0e0;
          }}
          
          .swagger-ui table tbody tr:hover {{
            background: #2a2a2a;
          }}
          
          .swagger-ui .tab {{
            color: #e0e0e0;
            border-bottom: 2px solid transparent;
          }}
          
          .swagger-ui .tab.active {{
            border-bottom-color: #5a8cc0;
            color: #5a8cc0;
          }}
        </style>
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-standalone-preset.js"></script>
        <script>
          window.onload = function() {{
            const ui = SwaggerUIBundle({{
              url: "{openapi_url}",
              dom_id: '#swagger-ui',
              deepLinking: true,
              presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIStandalonePreset
              ],
              plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
              ],
              layout: "StandaloneLayout",
              defaultModelsExpandDepth: 1,
              defaultModelExpandDepth: 1,
            }})
            window.ui = ui
          }}
        </script>
      </body>
    </html>
    """


# Create FastAPI application with custom Swagger UI styling
app = FastAPI(
    title="Jose Rodriguez OPEN Restaurant Reservation System",
    version=settings.app_version,
    description="Production-ready Restaurant Table Reservation System API",
    lifespan=lifespan,
    debug=settings.debug,
    swagger_ui_html=get_custom_swagger_ui_html,
)


# Include routers with versioning
app.include_router(
    tables.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    reservations.router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["health"])
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns:
        Status information
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
