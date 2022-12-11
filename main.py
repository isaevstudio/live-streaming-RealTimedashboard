from fastapi import FastAPI
from dbinsert import main as mainInsert
from dash_main import main as mainMain
from dash_drilled import main as mainDrilled
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(mainInsert.routerdb)
app.include_router(mainMain.routerMain)
app.include_router(mainDrilled.routerDrill)

app.mount("/static", StaticFiles(directory="static"), name="static")