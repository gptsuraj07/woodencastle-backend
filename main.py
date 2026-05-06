from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from database import test_connection, db
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timedelta
import os
import shutil
import json
from typing import Optional
from jose import jwt, JWTError

from scripts.optimize_images import process_images
from scripts.upload_to_r2 import upload_images

SECRET_KEY = "supersecretkey123"   # change later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# =========================
# 🧠 MODELS
# =========================
class Review(BaseModel):
    product_id: str
    name: str
    rating: int
    comment: str
    images: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =========================
# 🚀 APP INIT
# =========================
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await test_connection()


# =========================
# 🌐 CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/admin/login")
async def admin_login(username: str = Form(...), password: str = Form(...)):

    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": username})

    return {"access_token": token}

def verify_token(authorization: str = Header(...)):

    try:
        scheme, token = authorization.split()

        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload

    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# =========================
# 🏠 BASIC ROUTES
# =========================
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


# =========================
# ⭐ REVIEWS
# =========================
@app.post("/reviews")
async def create_review(review: Review):

    product = await db["products"].find_one({"id": review.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Invalid product")

    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Invalid rating")

    review.name = review.name.strip()
    review.comment = review.comment.strip()

    if not review.name or not review.comment:
        raise HTTPException(status_code=400, detail="Invalid input")

    review_dict = review.dict()
    await db["reviews"].insert_one(review_dict)

    return {"message": "Review added"}


@app.get("/reviews/{product_id}")
async def get_reviews(product_id: str):
    reviews = []

    cursor = db["reviews"].find(
        {"product_id": product_id}
    ).sort("created_at", -1)

    async for review in cursor:
        review["_id"] = str(review["_id"])
        reviews.append(review)

    return reviews


# =========================
# 🛠️ ADMIN - CREATE PRODUCT
# =========================
@app.post("/admin/castle-products")
async def create_product(
    name: str = Form(...),

    parentCategory: str = Form(...),
    subCategory: str = Form(...),

    description: str = Form(...),
    variants: str = Form(...),

    files: List[UploadFile] = File(...),

    user: dict = Depends(verify_token)
):
    try:

        temp_input = "temp/raw"
        temp_output = "temp/optimized"

        shutil.rmtree(temp_input, ignore_errors=True)
        shutil.rmtree(temp_output, ignore_errors=True)

        os.makedirs(temp_input, exist_ok=True)
        os.makedirs(temp_output, exist_ok=True)

        # =========================
        # SAVE RAW FILES
        # =========================
        for f in files:

            path = os.path.join(temp_input, f.filename)

            with open(path, "wb") as fp:
                fp.write(await f.read())

        # =========================
        # PRODUCT ID
        # =========================
        product_id = name.lower().strip().replace(" ", "-")

        # =========================
        # OPTIMIZE IMAGES
        # =========================
        process_images(temp_input, temp_output)

        # =========================
        # UPLOAD TO R2
        # =========================
        image_urls = upload_images(
            temp_output,
            subCategory,
            product_id
        )

        # =========================
        # VARIANTS
        # =========================
        variants_list = json.loads(variants)

        # =========================
        # PRODUCT OBJECT
        # =========================
        product = {

            "id": product_id,

            "name": name,

            "parentCategory": parentCategory,
            "subCategory": subCategory,

            "description": description,

            "images": image_urls,

            "variants": variants_list
        }

        # =========================
        # INSERT
        # =========================
        result = await db["products"].insert_one(product)

        product["_id"] = str(result.inserted_id)

        # =========================
        # CLEANUP
        # =========================
        shutil.rmtree(temp_input, ignore_errors=True)
        shutil.rmtree(temp_output, ignore_errors=True)

        return {
            "message": "Product created",
            "product": product
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# 🗑️ DELETE PRODUCT
# =========================
from fastapi import Depends

@app.delete("/admin/delete-product/{product_id}")
async def delete_product(
    product_id: str,
    user: dict = Depends(verify_token)   # 👈 ADD THIS LINE
):
    result = await db["products"].delete_one({"id": product_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted successfully"}



# =========================
# 🗺️ SITEMAP
# =========================
@app.get("/sitemap.xml")
async def sitemap():

    products = await db["products"].find().to_list(None)

    urls = ""

    # =========================
    # STATIC PAGES
    # =========================
    static_pages = [
        "",
        "/products",
        "/about",
        "/contact"
    ]

    for page in static_pages:

        urls += f"""
        <url>
            <loc>https://thewoodencastle.com{page}</loc>
        </url>
        """


    # =========================
    # PRODUCT PAGES
    # =========================
    for product in products:

        product_id = product.get("id")

        if product_id:

            urls += f"""
            <url>
                <loc>https://thewoodencastle.com/products/{product_id}</loc>
            </url>
            """

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
"""

    return Response(
        content=xml_content,
        media_type="application/xml"
    )


# =========================
# ✏️ UPDATE PRODUCT (NO IMAGE CHANGE)
# =========================
@app.put("/admin/update-product/{product_id}")
async def update_product(

    product_id: str,

    name: str = Form(...),

    parentCategory: str = Form(...),
    subCategory: str = Form(...),

    description: str = Form(...),

    variants: str = Form(...),

    existing_images: str = Form(...),

    files: Optional[List[UploadFile]] = File(None),

    user: dict = Depends(verify_token)

):
    try:

        existing = await db["products"].find_one({"id": product_id})

        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

        # =========================
        # VARIANTS
        # =========================
        variants_raw = json.loads(variants)

        normalized_variants = []

        for v in variants_raw:

            normalized_variants.append({
                "label": v.get("label") or v.get("type") or "Default",
                "price": float(v.get("price", 0)),
                "dimensions": v.get("dimensions", "")
            })

        # =========================
        # IMAGES
        # =========================
        existing_images_list = json.loads(existing_images)

        image_urls = existing_images_list

        if files and len(files) > 0:

            temp_input = "temp/raw"
            temp_output = "temp/optimized"

            shutil.rmtree(temp_input, ignore_errors=True)
            shutil.rmtree(temp_output, ignore_errors=True)

            os.makedirs(temp_input, exist_ok=True)
            os.makedirs(temp_output, exist_ok=True)

            for f in files:

                path = os.path.join(temp_input, f.filename)

                with open(path, "wb") as fp:
                    fp.write(await f.read())

            process_images(temp_input, temp_output)

            image_urls = upload_images(
                temp_output,
                subCategory,
                product_id
            )

        # =========================
        # UPDATED DATA
        # =========================
        updated_data = {

            "name": name,

            "parentCategory": parentCategory,
            "subCategory": subCategory,

            "description": description,

            "variants": normalized_variants,

            "images": image_urls
        }

        # =========================
        # UPDATE DB
        # =========================
        await db["products"].update_one(
            {"id": product_id},
            {"$set": updated_data}
        )

        return {
            "message": "Product updated successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))