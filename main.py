from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()

OPEN_API_URL = "http://apis.data.go.kr/6260000/BusanLibraryInfoService/getBusanLibraryInfo"
SERVICE_KEY = "HeP7B7zv3%2FC7THy9IEYOodNvb0X%2FSaXiT2lu4J240dzlMt5e8BXORjYR0lEoRKoX4uK8bR%2FcqUUv7Jg8IP7wzw%3D%3D"

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATABASE = "libraries.db"

def initialize_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        region TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()


def get_libraries_by_region(region: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM library WHERE region = ?", (region,))
    results = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "name": row[1], "address": row[2], "region": row[3]} for row in results]


# 데이터베이스 초기화
@app.on_event("startup")
def startup_event():
    initialize_database()


# 페이지 렌더링
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 지역별 도서관 검색
@app.post("/search", response_class=HTMLResponse)
def search_libraries(request: Request, region: str = Form(...)):
    libraries = get_libraries_by_region(region)
    return templates.TemplateResponse("results.html", {"request": request, "libraries": libraries, "region": region})
