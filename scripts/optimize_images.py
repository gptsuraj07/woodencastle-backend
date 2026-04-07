import os
from PIL import Image

# =========================
# 📂 CONFIG
# =========================
INPUT_FOLDER = r"D:\products\raw-images\home-decor"
OUTPUT_FOLDER = r"D:\products\optimized-images\home-decor"

MAX_WIDTH = 600      # change to 400 if needed
QUALITY = 75         # reduce to 65 if size is still high

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png")


# =========================
# 🛠️ IMAGE OPTIMIZATION
# =========================
def optimize_image(input_path, output_path):
    try:
        with Image.open(input_path) as img:

            # Convert to RGB (required for WebP)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Resize (only if needed)
            width, height = img.size
            if width > MAX_WIDTH:
                new_height = int((MAX_WIDTH / width) * height)
                img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Save as WebP
            img.save(output_path, "WEBP", quality=QUALITY, optimize=True)

            size_kb = os.path.getsize(output_path) // 1024
            print(f"✅ {input_path} → {size_kb} KB")

    except Exception as e:
        print(f"❌ ERROR: {input_path} | {e}")


# =========================
# 🔁 PROCESS ALL FILES
# =========================
def process_all_images():
    total = 0

    for root, _, files in os.walk(INPUT_FOLDER):
        for file in files:

            if not file.lower().endswith(SUPPORTED_FORMATS):
                continue

            input_path = os.path.join(root, file)

            # Preserve folder structure
            relative_path = os.path.relpath(input_path, INPUT_FOLDER)

            # Change extension to .webp
            output_relative = os.path.splitext(relative_path)[0] + ".webp"

            output_path = os.path.join(OUTPUT_FOLDER, output_relative)

            # Skip if already exists
            if os.path.exists(output_path):
                print(f"⏭️ Skipped (already exists): {output_path}")
                continue

            optimize_image(input_path, output_path)
            total += 1

    print(f"\n🎯 DONE: {total} images processed")


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    process_all_images()