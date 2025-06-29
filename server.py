from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from handlers.oauth_handler import OAuthManager

app = FastAPI()
oauth_manager = OAuthManager()

@app.get("/auth")
async def auth():
    """
    Перенаправляет пользователя на страницу авторизации Google.
    """
    auth_url, state = oauth_manager.get_auth_url()
    return RedirectResponse(auth_url)

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    """
    Обрабатывает redirect от Google после успешной авторизации.
    """
    code = request.query_params.get("code")
    error = request.query_params.get("error")

    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="No code provided in callback")

    creds = oauth_manager.fetch_tokens(code)

    print(f"Access token: {creds.token}")
    print(f"Refresh token: {creds.refresh_token}")

    return HTMLResponse(content="""
    <html>
        <head><title>Авторизация завершена!</title></head>
        <body>
            <h2>✅ Авторизация прошла успешно!</h2>
            <p>Можете вернуться в Telegram-бота.</p>
        </body>
    </html>
    """)
