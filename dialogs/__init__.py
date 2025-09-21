# dialogs/__init__.py

from .account import AddAccountDialog, EditAccountDialog, ImportAccountsDialog
from .page import AddPageDialog, EditPageDialog, AdvancedBulkAddPagesDialog, ScheduleDetailDialog, EditScheduleDialog
from .bulk_edit import BulkEditAccountsDialog, BulkEditPagesDialog, BulkProxyDialog
from .recycle_bin import RecycleBinDialog, ConfirmDeleteDialog
from .settings import ColumnSettingsDialog
from .utility import (NoteDialog, CompleterDelegate)