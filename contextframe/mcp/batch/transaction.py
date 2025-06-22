"""Transaction support for atomic batch operations."""

import logging
from collections.abc import Callable
from contextframe.frame import FrameDataset, FrameRecord
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class Operation:
    """Represents a single operation in a transaction."""

    op_type: str  # 'add', 'update', 'delete'
    data: Any
    rollback_data: Any = None


@dataclass
class BatchTransaction:
    """Manages atomic batch operations with rollback support.

    Provides transaction semantics for batch operations on FrameDataset.
    If any operation fails, all completed operations are rolled back.
    """

    dataset: FrameDataset
    operations: list[Operation] = field(default_factory=list)
    completed_ops: list[tuple[int, Operation]] = field(default_factory=list)

    def add_operation(self, op_type: str, data: Any, rollback_data: Any = None):
        """Add an operation to the transaction.

        Args:
            op_type: Type of operation ('add', 'update', 'delete')
            data: Data for the operation
            rollback_data: Data needed to undo the operation
        """
        self.operations.append(Operation(op_type, data, rollback_data))

    async def commit(self) -> dict[str, Any]:
        """Execute all operations atomically.

        Returns:
            Summary of transaction results

        Raises:
            Exception: If any operation fails (after rollback)
        """
        try:
            for i, op in enumerate(self.operations):
                await self._execute_operation(op)
                self.completed_ops.append((i, op))

            return {
                "success": True,
                "operations_completed": len(self.completed_ops),
                "total_operations": len(self.operations),
            }

        except Exception as e:
            logger.error(
                f"Transaction failed at operation {len(self.completed_ops)}: {e}"
            )
            await self.rollback()
            raise TransactionError(
                f"Transaction rolled back due to: {e}",
                completed=len(self.completed_ops),
                total=len(self.operations),
            )

    async def rollback(self):
        """Undo all completed operations."""
        logger.info(f"Rolling back {len(self.completed_ops)} operations")

        # Rollback in reverse order
        for i, op in reversed(self.completed_ops):
            try:
                await self._rollback_operation(op)
            except Exception as e:
                logger.error(f"Failed to rollback operation {i} ({op.op_type}): {e}")
                # Continue rollback despite errors

    async def _execute_operation(self, op: Operation):
        """Execute a single operation."""
        if op.op_type == "add":
            if isinstance(op.data, list):
                self.dataset.add_many(op.data)
            else:
                self.dataset.add(op.data)

        elif op.op_type == "update":
            # For update, data should be (record_id, updated_record)
            record_id, updated_record = op.data

            # Store original for rollback
            if op.rollback_data is None:
                original = self.dataset.get(record_id)
                op.rollback_data = original

            # Delete and re-add (Lance pattern)
            self.dataset.delete(record_id)
            self.dataset.add(updated_record)

        elif op.op_type == "delete":
            # For delete, data is the record ID
            record_id = op.data

            # Store record for rollback
            if op.rollback_data is None:
                original = self.dataset.get(record_id)
                op.rollback_data = original

            self.dataset.delete(record_id)

        else:
            raise ValueError(f"Unknown operation type: {op.op_type}")

    async def _rollback_operation(self, op: Operation):
        """Rollback a single operation."""
        if op.op_type == "add":
            # Undo add by deleting
            if isinstance(op.data, list):
                for record in op.data:
                    try:
                        self.dataset.delete(record.id)
                    except:
                        pass  # Record may not exist
            else:
                try:
                    self.dataset.delete(op.data.id)
                except:
                    pass

        elif op.op_type == "update":
            # Restore original record
            if op.rollback_data:
                record_id = op.data[0]
                try:
                    self.dataset.delete(record_id)
                except:
                    pass
                self.dataset.add(op.rollback_data)

        elif op.op_type == "delete":
            # Restore deleted record
            if op.rollback_data:
                self.dataset.add(op.rollback_data)


class TransactionError(Exception):
    """Error during transaction execution."""

    def __init__(self, message: str, completed: int, total: int):
        super().__init__(message)
        self.completed = completed
        self.total = total
