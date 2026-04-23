# Legacy Audit

## Files Audited
- Legacy source: `C:\Users\Windows\Downloads\Botshop-main\Botshop-main\1.py`
- Legacy config: `C:\Users\Windows\Downloads\Botshop-main\Botshop-main\tele_shop_config.json`
- Legacy docs: `C:\Users\Windows\Downloads\Botshop-main\Botshop-main\README.md`
- Legacy dependencies: `C:\Users\Windows\Downloads\Botshop-main\Botshop-main\requirements.txt`
- Legacy runner: `C:\Users\Windows\Downloads\Botshop-main\Botshop-main\setup.bat`
- Legacy database: `C:\Users\Windows\Downloads\Botshop-main\Botshop-main\tele_shop.sqlite3`

## Legacy Features
- User commands: `/start`, `/help`, `/getchatid`, `/checkadmin`.
- User menu: categories, deposit, order history, affiliate, hidden admin button.
- User shopping flow: category list, product list, product detail, buy now, coupon yes/no, coupon input, balance deduction, stock deduction, order creation, deliver text.
- Referral flow: `start=ref_<user_id>`, `ref_by` assigned once, affiliate percentage per referrer, commission credited on successful purchase.
- Start media flow: optional start video sent on `/start`.
- Admin commands: add/edit/delete category, add/edit/delete product, create/update coupon, disable coupon, set affiliate percentage, broadcast.
- Admin inline panel: shortcuts for all admin commands.
- Deposit flow: user enters amount, bot generates VietQR, creates pending deposit, admin receives approve/reject buttons.
- Manual deposit review: approve credits balance and creates deposit row, reject marks request rejected.
- Auto bank polling: polls Coderent API, filters `IN` transactions, parses `Napid <user_id>`, credits balance, records deposits, stores transaction IDs in `bank_seen`.
- Logging: admin direct messages for purchases/deposits, log group messages for successful purchases and deposits.
- Desktop GUI: dark theme, load/save config, start/stop app, real-time logs, bank config fields.

## Legacy Schema
- Business tables detected: `users`, `categories`, `products`, `orders`, `deposits`, `coupons`, `affiliate`, `affiliate_earnings`, `bank_seen`.
- Code expected `pending_deposits`, but the shipped SQLite file did not contain that table.

## Feature Mapping: Legacy -> New Modules
- Legacy command handlers -> `app/bot/handlers.py`
- Legacy inline keyboards -> `app/bot/keyboards.py`
- Legacy text assembly -> `app/bot/text.py`
- Legacy config dataclass/json -> `app/config/settings.py`, `app/config/loader.py`
- Legacy SQLite helpers -> `app/db/connection.py`, `app/db/migrations.py`, `app/db/repositories/*`
- Legacy order logic -> `app/services/order_service.py`
- Legacy coupon logic -> `app/services/coupon_service.py`
- Legacy affiliate logic -> `app/services/affiliate_service.py`
- Legacy deposit/manual approval logic -> `app/services/deposit_service.py`
- Legacy VietQR URL builder -> `app/payments/vietqr.py`
- Legacy bank polling -> `app/payments/bank_client.py`, `app/payments/bank_poller.py`
- Legacy GUI runner -> `app/gui/app_gui.py`
- Legacy start/stop lifecycle -> `app/runtime.py`, `app/bot/application.py`
- Legacy setup/migration/backup -> `scripts/run_gui.py`, `scripts/run_bot.py`, `scripts/migrate_legacy.py`, `scripts/backup_db.py`

## Bugs / Risks / Technical Debt Found In Legacy Code
- Secrets were hardcoded in `tele_shop_config.json` and must be rotated.
- `pending_deposits` table was missing from the shipped SQLite database although the code used it.
- Purchase flow was non-atomic: balance deduction, stock deduction, coupon usage and affiliate credit happened in separate DB operations.
- Race condition: two buyers could pass stock and balance checks concurrently and oversell the last stock item.
- Double-credit risk: manual deposit approval and bank polling could both credit the same logical deposit.
- Coupon usage increment was not concurrency-safe.
- `bank_seen` deduplication happened before semantic validation, but no reconciliation existed with manual approvals.
- Many messages had mojibake/encoding corruption.
- Admin panel only instructed admins to run commands; business logic still lived in the monolith file.
- Logging used ad-hoc strings instead of structured logger levels.
- Config validation was shallow; GUI accepted obviously broken polling values and missing payment fields.
- Start/stop lifecycle tied bot and bank polling together; no separate runtime control.
- No test coverage for financial or coupon logic.

## Architecture Decision
- Keep Python + `python-telegram-bot` + `customtkinter` to preserve runtime model and Windows GUI support.
- Keep SQLite for backward compatibility, but wrap it with WAL mode, migrations, repositories and explicit transactions.
- Split business logic into services so Telegram handlers and GUI remain orchestration layers.
- Add runtime controller so GUI and headless scripts use the same container, services and safety checks.

