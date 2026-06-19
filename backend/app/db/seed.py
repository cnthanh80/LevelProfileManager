from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.information_system import InformationSystem
from app.models.level_profile import LevelProfile
from app.models.organization import Organization
from app.models.role import Role
from app.models.security_requirement import SecurityRequirement
from app.models.user import User

ROLES = [
    ("ADMIN", "Quản trị hệ thống", "Toàn quyền cấu hình và quản trị người dùng"),
    ("SECURITY_OFFICER", "Cán bộ ATTT", "Tạo và cập nhật hồ sơ, checklist, minh chứng"),
    ("OPERATOR", "Đơn vị vận hành", "Cập nhật thông tin hệ thống theo phạm vi được giao"),
    ("REVIEWER", "Người rà soát", "Rà soát hồ sơ và ghi ý kiến"),
    ("APPROVER", "Lãnh đạo phê duyệt", "Phê duyệt nội bộ hồ sơ"),
    ("REPORT_VIEWER", "Người xem báo cáo", "Chỉ xem dashboard và báo cáo"),
]

SECURITY_REQUIREMENTS = [
    ("QL-001", "Ban hành chính sách an toàn thông tin", "Cơ quan/tổ chức ban hành chính sách ATTT áp dụng cho hệ thống thông tin.", "MANAGEMENT", "Chính sách ATTT", 1, True, 10),
    ("QL-002", "Phân công đầu mối phụ trách ATTT", "Có đầu mối, cán bộ hoặc bộ phận được giao trách nhiệm bảo đảm ATTT.", "MANAGEMENT", "Tổ chức ATTT", 1, True, 20),
    ("QL-003", "Quản lý tài khoản người dùng", "Có quy định cấp phát, thu hồi, rà soát tài khoản định kỳ.", "MANAGEMENT", "Quản lý truy cập", 1, True, 30),
    ("QL-004", "Sao lưu dữ liệu định kỳ", "Có quy định và thực hiện sao lưu phù hợp với yêu cầu vận hành.", "MANAGEMENT", "Sao lưu", 1, True, 40),
    ("KT-001", "Cơ chế xác thực người dùng", "Hệ thống có cơ chế xác thực trước khi truy cập chức năng nghiệp vụ.", "TECHNICAL", "Xác thực", 1, True, 50),
    ("KT-002", "Phân quyền truy cập theo vai trò", "Hệ thống kiểm soát quyền theo vai trò, nhiệm vụ hoặc phạm vi dữ liệu.", "TECHNICAL", "Phân quyền", 1, True, 60),
    ("QL-101", "Quy trình quản lý thay đổi", "Có quy trình tiếp nhận, phê duyệt, triển khai và ghi nhận thay đổi hệ thống.", "MANAGEMENT", "Quản lý thay đổi", 2, True, 110),
    ("QL-102", "Kế hoạch ứng cứu sự cố", "Có phương án tiếp nhận, phân loại, xử lý và báo cáo sự cố ATTT.", "MANAGEMENT", "Ứng cứu sự cố", 2, True, 120),
    ("KT-101", "Ghi nhật ký hệ thống", "Hệ thống ghi nhận nhật ký truy cập, lỗi và thao tác quản trị quan trọng.", "TECHNICAL", "Logging", 2, True, 130),
    ("KT-102", "Bảo vệ chống mã độc", "Máy chủ/máy trạm liên quan có biện pháp phòng chống mã độc phù hợp.", "TECHNICAL", "Anti Malware", 2, True, 140),
    ("QL-201", "Đánh giá rủi ro ATTT", "Thực hiện nhận diện, đánh giá và xử lý rủi ro ATTT cho hệ thống.", "MANAGEMENT", "Quản lý rủi ro", 3, True, 210),
    ("QL-202", "Rà soát quyền truy cập định kỳ", "Định kỳ rà soát tài khoản, quyền đặc quyền và quyền truy cập dữ liệu quan trọng.", "MANAGEMENT", "Quản lý truy cập", 3, True, 220),
    ("KT-201", "Tường lửa bảo vệ vùng mạng", "Triển khai tường lửa hoặc thiết bị kiểm soát truy cập mạng giữa các vùng.", "TECHNICAL", "An toàn mạng", 3, True, 230),
    ("KT-202", "Giám sát và cảnh báo ATTT", "Có giải pháp giám sát, cảnh báo sự kiện bất thường và sự kiện ATTT quan trọng.", "TECHNICAL", "Giám sát", 3, True, 240),
    ("KT-203", "Mã hóa kênh truyền", "Các kênh truyền qua mạng công cộng hoặc bên thứ ba sử dụng cơ chế mã hóa phù hợp.", "TECHNICAL", "Mã hóa", 3, True, 250),
    ("QL-301", "Kế hoạch duy trì hoạt động liên tục", "Có kế hoạch duy trì hoạt động, phục hồi sau sự cố phù hợp với mức độ quan trọng.", "MANAGEMENT", "BCP/DR", 4, True, 310),
    ("QL-302", "Diễn tập ứng cứu sự cố định kỳ", "Tổ chức diễn tập ứng cứu sự cố, khôi phục hệ thống định kỳ.", "MANAGEMENT", "Ứng cứu sự cố", 4, True, 320),
    ("KT-301", "Phân vùng mạng nhiều lớp", "Thiết kế phân vùng mạng cho người dùng, ứng dụng, CSDL, quản trị và DMZ.", "TECHNICAL", "An toàn mạng", 4, True, 330),
    ("KT-302", "Quản lý đặc quyền quản trị", "Tài khoản đặc quyền được kiểm soát, ghi log, rà soát và hạn chế dùng chung.", "TECHNICAL", "PAM", 4, True, 340),
    ("KT-303", "Sao lưu chống ransomware", "Bản sao lưu quan trọng có cơ chế bảo vệ khỏi sửa/xóa trái phép và kiểm thử phục hồi.", "TECHNICAL", "Backup", 4, True, 350),
    ("QL-401", "Trung tâm giám sát hoặc điều phối ATTT", "Có khả năng giám sát tập trung và điều phối xử lý sự kiện ATTT nghiêm trọng.", "MANAGEMENT", "SOC", 5, True, 410),
    ("KT-401", "Giám sát nâng cao và tương quan sự kiện", "Tương quan log/sự kiện từ nhiều nguồn để phát hiện tấn công có chủ đích.", "TECHNICAL", "SIEM", 5, True, 420),
]

SAMPLE_SYSTEMS = [
    ("HTTT-MB", "Hệ thống Mobile Banking", 3, "production", "hybrid", "Hệ thống phục vụ giao dịch khách hàng qua kênh di động"),
    ("HTTT-TTBC", "Hệ thống thông tin báo cáo", 2, "production", "on_premise", "Hệ thống tổng hợp báo cáo điều hành nội bộ"),
    ("HTTT-CORE", "Hệ thống Core Banking", 4, "production", "on_premise", "Hệ thống lõi xử lý giao dịch nghiệp vụ trọng yếu"),
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
            db.flush()

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
            db.flush()

        for code, title, description, group_name, category, required_level, is_mandatory, sort_order in SECURITY_REQUIREMENTS:
            req = db.scalar(select(SecurityRequirement).where(SecurityRequirement.code == code))
            if not req:
                db.add(SecurityRequirement(
                    code=code,
                    title=title,
                    description=description,
                    group_name=group_name,
                    category=category,
                    required_level=required_level,
                    is_mandatory=is_mandatory,
                    sort_order=sort_order,
                ))

        for code, name, level, environment, deployment_model, purpose in SAMPLE_SYSTEMS:
            system = db.scalar(select(InformationSystem).where(InformationSystem.code == code))
            if not system:
                system = InformationSystem(
                    code=code,
                    name=name,
                    owner_org_id=default_org.id,
                    operator_org_id=default_org.id,
                    manager_user_id=officer.id,
                    purpose=purpose,
                    scope="Phạm vi kiểm thử dữ liệu mẫu cho MVP",
                    main_functions="Quản lý nghiệp vụ, tra cứu, báo cáo, tích hợp API",
                    user_groups="Cán bộ nghiệp vụ, cán bộ vận hành, quản trị hệ thống",
                    data_types="Dữ liệu nghiệp vụ, dữ liệu người dùng, log hệ thống",
                    importance_level="high" if level >= 3 else "medium",
                    deployment_model=deployment_model,
                    environment=environment,
                    operation_status="active",
                    proposed_level=level,
                )
                db.add(system)
                db.flush()
            profile_code = f"HSCD-{code}-{level}"
            profile = db.scalar(select(LevelProfile).where(LevelProfile.profile_code == profile_code))
            if not profile:
                db.add(LevelProfile(
                    profile_code=profile_code,
                    information_system_id=system.id,
                    proposed_level=level,
                    status="DRAFT",
                    basis_for_level=f"Căn cứ mức độ ảnh hưởng khi mất an toàn thông tin, đề xuất cấp độ {level}.",
                    system_scope_description="Phạm vi gồm ứng dụng, máy chủ, CSDL, thiết bị mạng, kết nối nội bộ và kết nối bên thứ ba.",
                    technical_architecture="Kiến trúc nhiều lớp gồm lớp người dùng, ứng dụng, cơ sở dữ liệu, tích hợp và giám sát.",
                    confidentiality_impact="Ảnh hưởng đến bí mật dữ liệu nghiệp vụ và dữ liệu người dùng.",
                    integrity_impact="Ảnh hưởng đến tính đúng đắn của giao dịch, báo cáo và dữ liệu vận hành.",
                    availability_impact="Ảnh hưởng đến khả năng cung cấp dịch vụ và hoạt động nghiệp vụ.",
                    created_by=officer.id,
                ))

        db.commit()
        print("Seed data completed")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
