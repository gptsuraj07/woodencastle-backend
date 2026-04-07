
# R2_ENDPOINT = "https://5201539b1d894661ac78d7ee4a05b560.r2.cloudflarestorage.com/wooden-store-images"
# ACCESS_KEY = "595cd486cde27a0402888d165f4d6aed"
# SECRET_KEY = "17a63e1416aadb9691abafbda27332bfb42eb288f3d347f6176651936b3f0eb9"

import os
import boto3

# =========================
# 🔑 CONFIG
# =========================
R2_ENDPOINT = "https://5201539b1d894661ac78d7ee4a05b560.r2.cloudflarestorage.com"
ACCESS_KEY = "595cd486cde27a0402888d165f4d6aed"
SECRET_KEY = "17a63e1416aadb9691abafbda27332bfb42eb288f3d347f6176651936b3f0eb9"
BUCKET_NAME = "wooden-store-images"

# ONLY process this category
BASE_FOLDER = r"D:\products\optimized-images\home-decor"
CATEGORY = "home-decor"

# =========================
# 🔌 CONNECT
# =========================
s3 = boto3.client(
    "s3",
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

# =========================
# 🔍 CHECK IF FILE EXISTS
# =========================
def file_exists(key):
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except:
        return False


# =========================
# 🚀 UPLOAD ONLY NEW FILES
# =========================
def upload_new_images():

    print(f"\n🚀 Uploading ONLY NEW images for {CATEGORY}...\n")

    uploaded = 0
    skipped = 0

    for root, _, files in os.walk(BASE_FOLDER):
        for file in files:

            if not file.endswith(".webp"):
                continue

            file_path = os.path.join(root, file)

            # relative path from spice-stand folder
            relative_path = os.path.relpath(file_path, BASE_FOLDER)

            key = f"products/{CATEGORY}/{relative_path.replace(os.sep, '/')}"

            # 🔴 Skip if already exists in R2
            if file_exists(key):
                print(f"⏭️ Skipped (exists): {key}")
                skipped += 1
                continue

            with open(file_path, "rb") as f:
                s3.upload_fileobj(
                    f,
                    BUCKET_NAME,
                    key,
                    ExtraArgs={"ContentType": "image/webp"}
                )

            print(f"✔ Uploaded: {key}")
            uploaded += 1

    print(f"\n✅ Uploaded: {uploaded}")
    print(f"⏭️ Skipped: {skipped}")


# =========================
# ▶ RUN
# =========================
if __name__ == "__main__":
    upload_new_images()
    print("\n🎯 DONE (no deletions, only new uploads)")