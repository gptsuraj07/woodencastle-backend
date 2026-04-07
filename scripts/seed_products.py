import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# =========================
# 🔑 DB CONFIG
# =========================
MONGO_URL = "mongodb+srv://admin:test123@cluster0.ebxwyjk.mongodb.net/wooden_store?retryWrites=true&w=majority"

client = AsyncIOMotorClient(MONGO_URL)
db = client["wooden_store"]

CATEGORY = "home-decor"

BASE_URL = "https://pub-24d59b619a5d44d89b64faefe2bf26ca.r2.dev/products/home-decor"

# =========================
# 🧠 PRODUCTS (DIRECT INSERT)
# =========================
PRODUCTS = [
    {
        "id": "home-decor-towel-holder",
        "name": "Wooden Towel Holder",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/towel-holder/1.webp",
            f"{BASE_URL}/towel-holder/2.webp"
        ],
        "variants": [
            {
                "type": "Standard",
                "dimensions": "Height 3ft, Length 2.5ft, Width 1ft",
                "price": 4975
            }
        ],
        "description": "African teak wood towel holder made with pure solid wood. Durable and premium finish."
    },
    {
        "id": "home-decor-wooden-ladder",
        "name": "Wooden Ladder",
        "category": CATEGORY,
        "images": [
            f"{BASE_URL}/wooden-ladder/1.webp",
            f"{BASE_URL}/wooden-ladder/2.webp"
        ],
        "variants": [
            {
                "type": "Standard",
                "dimensions": "Height 4ft, Width 2.5ft",
                "price": 2575
            }
        ],
        "description": "Teak wood ladder with natural finish. Ideal for decor and towel hanging."
    }
]

# =========================
# 🚀 INSERT FUNCTION
# =========================
async def insert_home_decor():

    inserted = 0

    for product in PRODUCTS:

        # 🔴 Prevent duplicate insert
        exists = await db["products"].find_one({"id": product["id"]})

        if exists:
            print(f"⏭️ Skipped (already exists): {product['id']}")
            continue

        await db["products"].insert_one(product)
        print(f"✔ Inserted: {product['id']}")
        inserted += 1

    print(f"\n✅ DONE: {inserted} new products added")


# =========================
# ▶ RUN
# =========================
if __name__ == "__main__":
    asyncio.run(insert_home_decor())