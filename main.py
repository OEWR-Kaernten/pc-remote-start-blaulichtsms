import uvicorn
from decouple import config

if __name__ == "__main__":
    root_path = config("ROOT_PATH", default="")
    uvicorn.run("src.api:app", host="0.0.0.0", port=8080, reload=True, root_path=root_path)