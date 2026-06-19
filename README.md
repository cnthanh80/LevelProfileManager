# LevelProfileManager v2.2.3 Hotfix

Sửa lỗi Alembic revision quá dài gây lỗi PostgreSQL:

`value too long for type character varying(32)`

File migration cũ:

`backend/alembic/versions/0014_multi_organization_management.py`

được thay bằng:

`backend/alembic/versions/0014_multi_org.py`

Revision ID mới: `0014_multi_org`
