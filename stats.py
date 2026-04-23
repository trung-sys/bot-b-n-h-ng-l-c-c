from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_VIETQR_TEMPLATE = "compact2"
DEFAULT_DB_FILENAME = "tele_shop.sqlite3"
DEFAULT_CONFIG_FILENAME = "tele_shop_config.json"

VIETQR_BANKS: list[tuple[str, str]] = [
    ("Vietcombank", "vietcombank"),
    ("Techcombank", "techcombank"),
    ("MB Bank", "mbbank"),
    ("ACB", "acb"),
    ("VietinBank", "vietinbank"),
    ("BIDV", "bidv"),
    ("Sacombank", "sacombank"),
    ("TPBank", "tpbank"),
]

CODERENT_BANK_CODES: dict[str, str] = {
    "Vietcombank": "VCB",
    "MB Bank": "MB",
    "BIDV": "BIDV",
    "Techcombank": "TCB",
    "ACB": "ACB",
    "TPBank": "TPB",
    "VPBank": "VPB",
    "OCB": "OCB",
    "MSB": "MSB",
    "ViettelMoney": "VTM",
    "SeABank": "SEA",
    "TheSieuRe": "TSR",
}


@dataclass(slots=True)
class AppSettings:
    project_root: Path
    data_dir: Path
    exports_dir: Path
    logs_dir: Path
    db_path: Path
    config_path: Path
    admin_id: int = 0
    bot_token: str = ""
    log_group_id: int = 0
    start_video_path: str = ""
    vietqr_bank_name: str = "Vietcombank"
    vietqr_bank_id: str = "vietcombank"
    vietqr_stk: str = ""
    vietqr_ctk: str = ""
    vietqr_template: str = DEFAULT_VIETQR_TEMPLATE
    bank_api_name: str = "Vietcombank"
    bank_api_token: str = ""
    poll_interval_seconds: int = 15
    auto_bank_api_text: str = ""
    support_contact: str = ""
    maintenance_mode: bool = False
    deposit_expiry_minutes: int = 10
    history_limit: int = 15
    command_cooldown_seconds: int = 2
    bank_api_base_url: str = "https://api.coderent.one"

    def ensure_directories(self) -> None:
        self.project_root.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def validate_for_bot_start(self) -> list[str]:
        errors: list[str] = []
        if self.admin_id <= 0:
            errors.append("Chưa nhập Admin ID.")
        if not self.bot_token:
            errors.append("Chưa nhập Bot Token.")
        return errors

    def validate_for_bank_start(self) -> list[str]:
        errors: list[str] = []
        if not self.bank_api_token:
            errors.append("Chưa nhập Bank API Token.")
        if self.bank_api_name not in CODERENT_BANK_CODES:
            errors.append("Ngân hàng Bank API chưa được hỗ trợ.")
        if self.poll_interval_seconds < 5:
            errors.append("Poll interval phải từ 5 giây trở lên.")
        return errors

    def validate_vietqr(self) -> list[str]:
        errors: list[str] = []
        if not self.vietqr_stk:
            errors.append("Thiếu số tài khoản VietQR.")
        if not self.vietqr_ctk:
            errors.append("Thiếu chủ tài khoản VietQR.")
        if not self.vietqr_bank_id:
            errors.append("Thiếu mã ngân hàng VietQR.")
        return errors

    def to_persisted_dict(self) -> dict[str, object]:
        raw = asdict(self)
        for key in {"project_root", "data_dir", "exports_dir", "logs_dir", "db_path", "config_path"}:
            raw.pop(key, None)
        return raw

