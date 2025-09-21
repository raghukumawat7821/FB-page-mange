# database/__init__.py

# This file makes the 'database' folder a Python package and exposes all
# necessary functions for other parts of the application to use.

from .connection import create_tables
from .read import (
    get_table_data_for_export,
    get_all_accounts_data,
    get_total_accounts_count,
    get_all_pages_data,
    get_account_details,
    get_page_details_for_edit,
    get_all_accounts,
    get_unique_page_categories,
    get_unique_account_categories,
    get_profile_id_map,
    get_deleted_items,
    get_dependent_pages_count,
    check_duplicate,
    get_multiple_accounts_details,
    get_accounts_for_proxy_edit,
    get_multiple_pages_details
)
from .write import (
    wipe_and_restore_database,
    add_account,
    add_page,
    bulk_add_pages,
    bulk_import_accounts,
    update_account_details,
    bulk_update_accounts_partial,
    update_page_details,
    update_page_note,
    update_account_note,
    soft_delete,
    restore_item,
    permanently_delete_items,
    quick_edit_items,
    bulk_update_pages_partial
)