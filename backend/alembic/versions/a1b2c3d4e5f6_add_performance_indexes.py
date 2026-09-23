"""add_performance_indexes

Revision ID: a1b2c3d4e5f6
Revises: 87154d074e49
Create Date: 2026-09-23 02:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '87154d074e49'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Graph edges
    op.create_index('idx_graph_edges_src', 'graph_edges', ['source_id'], unique=False, if_not_exists=True)
    op.create_index('idx_graph_edges_tgt', 'graph_edges', ['target_id'], unique=False, if_not_exists=True)
    op.create_index('idx_graph_edges_src_tgt', 'graph_edges', ['source_id', 'target_id'], unique=False, if_not_exists=True)
    
    # Transaction inputs and outputs
    op.create_index('idx_tx_inputs_txid', 'transaction_inputs', ['transaction_id'], unique=False, if_not_exists=True)
    op.create_index('idx_tx_outputs_txid', 'transaction_outputs', ['transaction_id'], unique=False, if_not_exists=True)
    
    # Transactions & Wallets
    op.create_index('idx_transactions_ts', 'transactions', [sa.text('timestamp DESC')], unique=False, if_not_exists=True)
    op.create_index('idx_wallets_tx_cnt', 'wallets', [sa.text('tx_count DESC')], unique=False, if_not_exists=True)
    
    # Alerts
    op.create_index('idx_alerts_entity', 'alerts', ['entity_type', 'entity_id'], unique=False, if_not_exists=True)
    op.create_index('idx_alerts_created_at', 'alerts', [sa.text('created_at DESC')], unique=False, if_not_exists=True)
    op.create_index('idx_alerts_priority', 'alerts', ['priority'], unique=False, if_not_exists=True)
    op.create_index('idx_alerts_status', 'alerts', ['status'], unique=False, if_not_exists=True)
    
    # Audit Logs
    op.create_index('idx_audit_logs_created_at', 'audit_logs', [sa.text('created_at DESC')], unique=False, if_not_exists=True)


def downgrade() -> None:
    op.drop_index('idx_audit_logs_created_at', table_name='audit_logs', if_exists=True)
    op.drop_index('idx_alerts_status', table_name='alerts', if_exists=True)
    op.drop_index('idx_alerts_priority', table_name='alerts', if_exists=True)
    op.drop_index('idx_alerts_created_at', table_name='alerts', if_exists=True)
    op.drop_index('idx_alerts_entity', table_name='alerts', if_exists=True)
    op.drop_index('idx_wallets_tx_cnt', table_name='wallets', if_exists=True)
    op.drop_index('idx_transactions_ts', table_name='transactions', if_exists=True)
    op.drop_index('idx_tx_outputs_txid', table_name='transaction_outputs', if_exists=True)
    op.drop_index('idx_tx_inputs_txid', table_name='transaction_inputs', if_exists=True)
    op.drop_index('idx_graph_edges_src_tgt', table_name='graph_edges', if_exists=True)
    op.drop_index('idx_graph_edges_tgt', table_name='graph_edges', if_exists=True)
    op.drop_index('idx_graph_edges_src', table_name='graph_edges', if_exists=True)
