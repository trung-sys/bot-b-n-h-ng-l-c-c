from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from app.config.settings import AppSettings, DEFAULT_CONFIG_FILENAME, DEFAULT_DB_FILENAME, DEFAULT_VIETQR_TEMPLATE
from app.utils.validation import clamp, parse_bool, parse_int, safe_path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _get_env_or_json(env_key: str, json_data: dict[str, object], json_key: str, default: object) -> object:
    env_value = os.getenv(env_key)
    if env_value not in {None, ""}:
        return env_value
    return json_data.get(json_key, default)


def load_settings(project_root: Path | None = None) -> AppSettings:
    root = (project_root or get_project_root()).resolve()
    load_dotenv(root / ".env")

    data_dir = root / "data"
    exports_dir = root / "exports"
    logs_dir = root / "logs"
    config_path = data_dir / DEFAULT_CONFIG_FILENAME
    db_path = data_dir / DEFAULT_DB_FILENAME

    json_data: dict[str, object] = {}
    if config_path.exists():
        try:
            json_data = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            json_data = {}

    settings = AppSettings(
        project_root=root,
        data_dir=data_dir,
        exports_dir=exports_dir,
        logs_dir=logs_dir,
        db_path=db_path,
        config_path=config_path,
        admin_id=parse_int(_get_env_or_json("TELESHOP_ADMIN_ID", json_data, "admin_id", 0), 0),
        bot_token=str(_get_env_or_json("TELESHOP_BOT_TOKEN", json_data, "bot_token", "")),
        log_group_id=parse_int(_get_env_or_json("TELESHOP_LOG_GROUP_ID", json_data, "log_group_id", 0), 0),
        start_video_path=safe_path(_get_env_or_json("TELESHOP_START_VIDEO_PATH", json_data, "start_video_path", "")),
        vietqr_bank_name=str(_get_env_or_json("TELESHOP_VIETQR_BANK_NAME", json_data, "vietqr_bank_name", "Vietcombank")),
        vietqr_bank_id=str(_get_env_or_json("TELESHOP_VIETQR_BANK_ID", json_data, "vietqr_bank_id", "vietcombank")),
        vietqr_stk=str(_get_env_or_json("TELESHOP_VIETQR_STK", json_data, "vietqr_stk", "")),
        vietqr_ctk=str(_get_env_or_json("TELESHOP_VIETQR_CTK", json_data, "vietqr_ctk", "")),
        vietqr_template=str(_get_env_or_json("TELESHOP_VIETQR_TEMPLATE", json_data, "vietqr_template", DEFAULT_VIETQR_TEMPLATE)),
        bank_api_name=str(_get_env_or_json("TELESHOP_BANK_API_NAME", json_data, "bank_api_name", json_data.get("bank_v3_name", "Vietcombank"))),
        bank_api_token=str(_get_env_or_json("TELESHOP_BANK_API_TOKEN", json_data, "bank_api_token", json_data.get("bank_v3_token", ""))),
        poll_interval_seconds=clamp(
            parse_int(_get_env_or_json("TELESHOP_POLL_INTERVAL", json_data, "poll_interval_seconds", json_data.get("poll_interval", 15)), 15),
            5,
            3600,
        ),
        auto_bank_api_text=str(_get_env_or_json("TELESHOP_AUTO_BANK_API_TEXT", json_data, "auto_bank_api_text", "")),
        support_contact=str(_get_env_or_json("TELESHOP_SUPPORT_CONTACT", json_data, "support_contact", "")),
        maintenance_mode=parse_bool(_get_env_or_json("TELESHOP_MAINTENANCE_MODE", json_data, "maintenance_mode", False)),
        deposit_expiry_minutes=max(
            1,
            parse_int(_get_env_or_json("TELESHOP_DEPOSIT_EXPIRY_MINUTES", json_data, "deposit_expiry_minutes", 10), 10),
        ),
        history_limit=max(1, parse_int(_get_env_or_json("TELESHOP_HISTORY_LIMIT", json_data, "history_limit", 15), 15)),
        command_cooldown_seconds=max(
            0,
            parse_int(_get_env_or_json("TELESHOP_COMMAND_COOLDOWN_SECONDS", json_data, "command_cooldown_seconds", 2), 2),
        ),
        bank_api_base_url=str(_get_env_or_json("TELESHOP_BANK_API_BASE_URL", json_data, "bank_api_base_url", "https://api.coderent.one")),
    )
    settings.ensure_directories()
    return settings


def save_settings(settings: AppSettings) -> None:
    settings.ensure_directories()
    payload = settings.to_persisted_dict()
    settings.config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
