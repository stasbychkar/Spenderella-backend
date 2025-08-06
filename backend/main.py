from fastapi import FastAPI, Request, HTTPException
from backend.utils.plaid_utils import create_link_token, exchange_public_token, sync_all_transactions, sync_transactions_for_item, get_dashboard_data, get_transactions_data, update_transaction_category, get_categories_page_data, add_custom_category, edit_custom_category, delete_custom_category, get_accounts_page, delete_linked_account, create_demo_user, clone_demo_user
from backend.services.bank_item_service import save_bank_item
from backend.services.accounts_service import save_accounts
from backend.schemas.plaid_schemas import TokenModel, AccessModel, SyncRequestModel, UpdateCategoryRequest, AddCustomCategory, EditCustomCategory, DeleteLinkedAccount
from backend.utils.plaid_utils import sync_accounts
# import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from backend.db import sessionlocal
from backend.models import BankItem
from backend.utils.crypto import encrypt, decrypt
from backend.routers.webhook_router import webhook_router
from backend.utils.plaid_utils import USER_ID

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Later restrict to frontend origin.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register webhook router
app.include_router(webhook_router)

@app.get("/link-token")
def get_link_token():
    return create_link_token()

@app.post("/exchange-token")
def exchange_token(body: TokenModel):
    plaid_response = exchange_public_token(body.public_token)

    access_token = plaid_response["access_token"]
    access_token_encrypted = encrypt(access_token)
    plaid_item_id = plaid_response["item_id"]
    institution_name = body.institution_name
    user_id = USER_ID # hardcoded

    webhook_url = "https://fa07-2601-600-9380-ca0-4dc5-8b48-1a4e-4b57.ngrok-free.app/webhook"

    new_item = save_bank_item(
        user_id=user_id,
        plaid_item_id=plaid_item_id,
        access_token_encrypted=access_token_encrypted,
        institution_name=institution_name,
        webhook_url=webhook_url
    )

    # Sync and save accounts
    accounts = sync_accounts(access_token_encrypted)
    save_accounts(accounts, plaid_item_id, user_id)

    # Sync and save transactions
    sync_transactions_for_item(new_item, user_id)

    return {
        "message": "Bank item saved",
        "item_id": plaid_item_id,
    }

@app.post('/sync-all-transactions')
def sync_all():
    sync_all_transactions()
    return {"message": "Synced all transactions"}

# Database endpoints
# Dashboard
@app.get('/db-get-dashboard-page-data')
def db_get_dashboard_data(request: Request):
    demo_user_id = request.headers.get("x-demo-user-id")

    try:
        user_id = int(demo_user_id) if demo_user_id else USER_ID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid demo ID")

    return get_dashboard_data(user_id=user_id)

# Transactions
@app.get('/db-get-transactions-page-data')
def db_get_transactions_page_data(request: Request):
    demo_user_id = request.headers.get("x-demo-user-id")

    try:
        user_id = int(demo_user_id) if demo_user_id else USER_ID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid demo ID")
    return get_transactions_data(user_id=user_id)

@app.put('/db-update-transaction-category')
def db_update_transaction_category(req: UpdateCategoryRequest):
    return update_transaction_category(req)

# Categories
@app.get('/db-get-categories-page-data')
def db_get_categories_page_data(request: Request):
    demo_user_id = request.headers.get("x-demo-user-id")

    try:
        user_id = int(demo_user_id) if demo_user_id else USER_ID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid demo ID")
    return get_categories_page_data(user_id=user_id)

@app.put('/db-add-custom-category')
def db_add_custom_category(req: AddCustomCategory):
    return add_custom_category(req)

@app.put('/db-edit-custom-category')
def db_edit_custom_category(req: EditCustomCategory):
    return edit_custom_category(req)

@app.put('/db-delete-custom-category')
def db_delete_custom_category(req: EditCustomCategory):
    return delete_custom_category(req)

# Accounts
@app.get('/db-get-accounts-page')
def db_get_accounts_page(request: Request):
    demo_user_id = request.headers.get("x-demo-user-id")

    try:
        user_id = int(demo_user_id) if demo_user_id else USER_ID
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid demo ID")
    return get_accounts_page(user_id=user_id)

@app.put('/db-delete-linked_account')
def db_delete_linked_account(req: DeleteLinkedAccount):
    return delete_linked_account(req)

@app.post('/db-create-demo-user')
def db_create_demo_user():
    new_user = create_demo_user()
    clone_demo_user(new_user.id)
    return {"user_id": new_user.id}