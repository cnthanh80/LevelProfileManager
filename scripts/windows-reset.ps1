# Xóa container + volume DB để dựng lại từ đầu
# Cẩn thận: lệnh này xóa dữ liệu PostgreSQL local của project

docker compose down -v

docker compose up -d --build
