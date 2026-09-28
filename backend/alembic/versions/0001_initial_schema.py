"""Initial Material Master Schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-09-28 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. CPSE table
    op.create_table(
        'cpse',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )

    # 2. Materials table
    op.create_table(
        'materials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cpse_id', sa.Integer(), nullable=False),
        sa.Column('material_code', sa.String(length=100), nullable=False),
        sa.Column('original_description', sa.Text(), nullable=False),
        sa.Column('normalized_description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('source_reference', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cpse_id'], ['cpse.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_materials_cpse_code', 'materials', ['cpse_id', 'material_code'], unique=True)
    op.create_index('ix_materials_category_status', 'materials', ['category', 'status'])

    # 3. Material Attributes table
    op.create_table(
        'material_attributes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('material_type', sa.String(length=100), nullable=True),
        sa.Column('material', sa.String(length=100), nullable=True),
        sa.Column('grade', sa.String(length=100), nullable=True),
        sa.Column('size', sa.String(length=100), nullable=True),
        sa.Column('diameter', sa.Float(), nullable=True),
        sa.Column('length', sa.Float(), nullable=True),
        sa.Column('width', sa.Float(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('thickness', sa.Float(), nullable=True),
        sa.Column('pressure', sa.String(length=100), nullable=True),
        sa.Column('schedule', sa.String(length=50), nullable=True),
        sa.Column('form', sa.String(length=100), nullable=True),
        sa.Column('standard', sa.String(length=150), nullable=True),
        sa.Column('application', sa.String(length=200), nullable=True),
        sa.Column('manufacturer', sa.String(length=200), nullable=True),
        sa.Column('other_attributes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('material_id'),
    )

    # 4. Material Embeddings table
    op.create_table(
        'material_embeddings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('embedding', sa.JSON(), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('material_id'),
    )

    # 5. Material Matches table
    op.create_table(
        'material_matches',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_material_id', sa.Integer(), nullable=False),
        sa.Column('target_material_id', sa.Integer(), nullable=False),
        sa.Column('semantic_score', sa.Float(), nullable=False),
        sa.Column('fuzzy_score', sa.Float(), nullable=False),
        sa.Column('attribute_score', sa.Float(), nullable=False),
        sa.Column('technical_score', sa.Float(), nullable=False),
        sa.Column('final_score', sa.Float(), nullable=False),
        sa.Column('classification', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('review_required', sa.Boolean(), nullable=False),
        sa.Column('explanation', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_material_id'], ['materials.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_material_id'], ['materials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_match_source_target', 'material_matches', ['source_material_id', 'target_material_id'], unique=True)

    # 6. Material Conflicts table
    op.create_table(
        'material_conflicts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('attribute', sa.String(length=100), nullable=False),
        sa.Column('source_value', sa.String(length=255), nullable=True),
        sa.Column('target_value', sa.String(length=255), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['match_id'], ['material_matches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # 7. National Materials table
    op.create_table(
        'national_materials',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cnmc', sa.String(length=50), nullable=False),
        sa.Column('standard_description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('canonical_attributes', sa.JSON(), nullable=False),
        sa.Column('identity_hash', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cnmc'),
        sa.UniqueConstraint('identity_hash'),
    )

    # 8. CPSE Material Mapping table
    op.create_table(
        'cpse_material_mapping',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('national_material_id', sa.Integer(), nullable=False),
        sa.Column('cpse_id', sa.Integer(), nullable=False),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('mapping_type', sa.String(length=50), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['national_material_id'], ['national_materials.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['cpse_id'], ['cpse.id']),
        sa.ForeignKeyConstraint(['material_id'], ['materials.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cpse_material_mapping_nat_mat', 'cpse_material_mapping', ['national_material_id', 'material_id'], unique=True)

    # 9. Ingestion Jobs table
    op.create_table(
        'ingestion_jobs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('cpse_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('total_rows', sa.Integer(), nullable=False),
        sa.Column('processed_rows', sa.Integer(), nullable=False),
        sa.Column('accepted_rows', sa.Integer(), nullable=False),
        sa.Column('rejected_rows', sa.Integer(), nullable=False),
        sa.Column('warnings', sa.Integer(), nullable=False),
        sa.Column('errors', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cpse_id'], ['cpse.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('ingestion_jobs')
    op.drop_table('cpse_material_mapping')
    op.drop_table('national_materials')
    op.drop_table('material_conflicts')
    op.drop_table('material_matches')
    op.drop_table('material_embeddings')
    op.drop_table('material_attributes')
    op.drop_table('materials')
    op.drop_table('cpse')
