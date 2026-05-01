import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# =========================
# 🔑 DB CONFIG
# =========================
MONGO_URL = "mongodb+srv://admin:test123@cluster0.ebxwyjk.mongodb.net/wooden_store?retryWrites=true&w=majority"

client = AsyncIOMotorClient(MONGO_URL)
db = client["wooden_store"]

CATEGORY = "teak-wooden-boards"

BASE_URL = "https://pub-24d59b619a5d44d89b64faefe2bf26ca.r2.dev/products/teak-wooden-boards"

COMMON_DESC = "Made from solid single teak wood. No joinery. Chemical-free and completely food safe."

# =========================
# 🧠 PRODUCTS
# =========================
PRODUCTS = [

    {
        "id": "bat-teak-board",
        "name": "Bat Teak Board",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/bat-teak-board/1.webp",
            f"{BASE_URL}/bat-teak-board/2.webp"
        ],
        "price": 1375,
        "description": COMMON_DESC
    },

    {
        "id": "tag-teak-board",
        "name": "Tag Teak Board",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/tag-teak-board/1.webp",
            f"{BASE_URL}/tag-teak-board/2.webp"
        ],
        "price": 1375,
        "description": COMMON_DESC
    },

    {
        "id": "bread-teak-board",
        "name": "Bread Teak Board",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/bread-teak-board/1.webp",
            f"{BASE_URL}/bread-teak-board/2.webp"
        ],
        "price": 1475,
        "description": COMMON_DESC
    },

    {
        "id": "simple-teak-board",
        "name": "Simple Teak Board",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/simple-teak-board/1.webp",
            f"{BASE_URL}/simple-teak-board/2.webp"
        ],
        "price": 1675,
        "description": COMMON_DESC
    },

    {
        "id": "flat-sided-teak-board",
        "name": "Flat Sided Teak Board",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/flat-sided-teak-board/1.webp",
            f"{BASE_URL}/flat-sided-teak-board/2.webp"
        ],
        "price": 1375,
        "description": COMMON_DESC
    },

    {
        "id": "diamond-head-teak-board",
        "name": "Diamond Head Teak Board",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/diamond-head-teak-board/1.webp",
            f"{BASE_URL}/diamond-head-teak-board/2.webp"
        ],
        "price": 1275,
        "description": COMMON_DESC
    },

    {
        "id": "grooves-teak-board",
        "name": "Grooves Teak Board",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/grooves-teak-board/1.webp",
            f"{BASE_URL}/grooves-teak-board/2.webp"
        ],
        "price": 1375,
        "description": COMMON_DESC
    },

    {
        "id": "wave-teak-board",
        "name": "Wave Teak Board",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/wave-teak-board/1.webp",
            f"{BASE_URL}/wave-teak-board/2.webp"
        ],
        "price": 1375,
        "description": COMMON_DESC
    },

    {
        "id": "teak-butcher-block",
        "name": "Teak Butcher Block",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/teak-butcher-block/1.webp",
            f"{BASE_URL}/teak-butcher-block/2.webp"
        ],
        "price": 2375,
        "description": "Thick teak wood butcher block. Heavy-duty cutting surface. " + COMMON_DESC
    },

    {
        "id": "teak-big-board",
        "name": "Teak Big Board",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/teak-big-board/1.webp",
            f"{BASE_URL}/teak-big-board/2.webp",
            f"{BASE_URL}/teak-big-board/3.webp",
            f"{BASE_URL}/teak-big-board/4.webp"
        ],
        "price": 0,
        "description": COMMON_DESC
    }

]

# =========================
# 🚀 INSERT FUNCTION
# =========================
async def insert_teak_boards():

    inserted = 0

    for product in PRODUCTS:

        exists = await db["products"].find_one({"id": product["id"]})

        if exists:
            print(f"⏭️ Skipped: {product['id']}")
            continue

        await db["products"].insert_one(product)
        print(f"✔ Inserted: {product['id']}")
        inserted += 1

    print(f"\n✅ DONE: {inserted} new products added")


# =========================
# ▶ RUN
# =========================
if __name__ == "__main__":
    asyncio.run(insert_teak_boards())