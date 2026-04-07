from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import test_connection, db

app = FastAPI()

# ✅ STARTUP EVENT (AFTER app creation)
@app.on_event("startup")
async def startup_event():
    await test_connection()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
def home():
    return {"message": "Backend working"}

@app.get("/products")
async def get_products():
    products = []
    async for product in db["products"].find():
        product["_id"] = str(product["_id"])
        products.append(product)
    return products


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    product = await db["products"].find_one({"id": product_id})

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product["_id"] = str(product["_id"])
    return product