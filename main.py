import uvicorn
from decouple import config
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    root_path = config("ROOT_PATH", default="")
    uvicorn.run("src.api:app", host="0.0.0.0", port=8080, reload=True, root_path=root_path)