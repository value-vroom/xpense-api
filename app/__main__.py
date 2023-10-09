"""Main module for running the FastAPI app."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True, reload_dirs=["app"])
