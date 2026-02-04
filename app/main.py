from fastapi import FastAPI

app = FastAPI(title="Social API",
              version="0.1.0",)

@app.get("/")
async def health():
    return {"status": "ok"}