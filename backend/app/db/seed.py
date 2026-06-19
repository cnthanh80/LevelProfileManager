from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User

ROLES = [
    ("ADMIN", "Quản trị hệ thống", "Toàn quyền cấu hình và quản trị người dùng"),
    ("SECURITY_OFFICER", "Cán bộ ATTT", "Tạo và cập nhật hồ sơ, checklist, minh chứng"),
    ("OPERATOR", "Đơn vị vận hành", "Cập nhật thông tin hệ thống theo phạm vi được giao"),
    ("REVIEWER", "Người rà soát", "Rà soát hồ sơ và ghi ý kiến"),
    ("APPROVER", "Lãnh đạo phê duyệt", "Phê duyệt nội bộ hồ sơ"),
    ("REPORT_VIEWER", "Người xem báo cáo", "Chỉ xem dashboard và báo cáo"),
]


def seed() -> None:
    db = SessionLocal()
    try:
        default_org = db.scalar(select(Organization).where(Organization.code == "TTCNTT"))
        if not default_org:
            default_org = Organization(
                code="TTCNTT",
                name="Trung tâm Công nghệ thông tin",
                org_type="internal_unit",
                description="Đơn vị mặc định phục vụ kiểm thử MVP",
            )
            db.add(default_org)
            db.flush()

        role_map = {}
        for code, name, description in ROLES:
            role = db.scalar(select(Role).where(Role.code == code))
            if not role:
                role = Role(code=code, name=name, description=description)
                db.add(role)
                db.flush()
            role_map[code] = role

        admin = db.scalar(select(User).where(User.username == "admin"))
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.local",
                full_name="Quản trị hệ thống",
                hashed_password=get_password_hash("Admin@123"),
                role_id=role_map["ADMIN"].id,
                organization_id=default_org.id,
                is_active=True,
            )
            db.add(admin)

        officer = db.scalar(select(User).where(User.username == "attt"))
        if not officer:
            officer = User(
                username="attt",
                email="attt@example.local",
                full_name="Cán bộ an toàn thông tin",
                hashed_password=get_password_hash("Attt@123"),
                role_id=role_map["SECURITY_OFFICER"].id,
                organization_id=default_org.id,
                is_active=True,
            )
            db.add(officer)

        db.commit()
        print("Seed data completed")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
