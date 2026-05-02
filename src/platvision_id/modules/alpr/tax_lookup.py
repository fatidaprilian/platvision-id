from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from html import unescape
from html.parser import HTMLParser
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SUMSEL_TAX_SOURCE = "Bapenda Sumsel"
SUMSEL_TAX_URL = "https://bapenda.sumselprov.go.id/cek_pajak/t_ulang"
PLATE_PATTERN = re.compile(r"^\s*([A-Z]{1,2})\s+(\d{1,4})\s+([A-Z]{1,3})\s*$")


REFERENCE_SOURCES_BY_PREFIX = {
    "A": ("Bapenda Banten", "https://infopkb.bantenprov.go.id/"),
    "B": ("Samsat DKI Jakarta", "https://samsat-pkb2.jakarta.go.id/"),
    "D": ("Bapenda Jawa Barat", "https://bapenda.jabarprov.go.id/infopkb/"),
    "E": ("Bapenda Jawa Barat", "https://bapenda.jabarprov.go.id/infopkb/"),
    "F": ("Bapenda Jawa Barat", "https://bapenda.jabarprov.go.id/infopkb/"),
    "T": ("Bapenda Jawa Barat", "https://bapenda.jabarprov.go.id/infopkb/"),
    "Z": ("Bapenda Jawa Barat", "https://bapenda.jabarprov.go.id/infopkb/"),
    "G": ("Bapenda Jawa Tengah New Sakpole", "https://ppid.bapenda.jatengprov.go.id/page/new_sakpole"),
    "H": ("Bapenda Jawa Tengah New Sakpole", "https://ppid.bapenda.jatengprov.go.id/page/new_sakpole"),
    "K": ("Bapenda Jawa Tengah New Sakpole", "https://ppid.bapenda.jatengprov.go.id/page/new_sakpole"),
    "R": ("Bapenda Jawa Tengah New Sakpole", "https://ppid.bapenda.jatengprov.go.id/page/new_sakpole"),
    "AA": ("Bapenda Jawa Tengah New Sakpole", "https://ppid.bapenda.jatengprov.go.id/page/new_sakpole"),
    "AD": ("Bapenda Jawa Tengah New Sakpole", "https://ppid.bapenda.jatengprov.go.id/page/new_sakpole"),
    "L": ("Bapenda Jawa Timur e-Samsat", "https://info.dipendajatim.go.id/esamsat/"),
    "M": ("Bapenda Jawa Timur e-Samsat", "https://info.dipendajatim.go.id/esamsat/"),
    "N": ("Bapenda Jawa Timur e-Samsat", "https://info.dipendajatim.go.id/esamsat/"),
    "P": ("Bapenda Jawa Timur e-Samsat", "https://info.dipendajatim.go.id/esamsat/"),
    "S": ("Bapenda Jawa Timur e-Samsat", "https://info.dipendajatim.go.id/esamsat/"),
    "W": ("Bapenda Jawa Timur e-Samsat", "https://info.dipendajatim.go.id/esamsat/"),
    "AE": ("Bapenda Jawa Timur e-Samsat", "https://info.dipendajatim.go.id/esamsat/"),
    "AG": ("Bapenda Jawa Timur e-Samsat", "https://info.dipendajatim.go.id/esamsat/"),
}


class TaxLookup(Protocol):
    def lookup(self, normalized_plate: str) -> dict[str, object]:
        ...


@dataclass(frozen=True)
class TaxLookupResult:
    supported: bool
    status: str
    source: str
    source_url: str
    message: str
    payment_status: str | None = None
    registered_plate: str | None = None
    owner_name: str | None = None
    owner_address: str | None = None
    tax_due_date: str | None = None
    stnk_expiry_date: str | None = None
    vehicle_type: str | None = None
    vehicle_brand: str | None = None
    vehicle_model: str | None = None
    vehicle_year: str | None = None
    vehicle_color: str | None = None
    pkb_principal: str | None = None
    pkb_penalty: str | None = None
    pkb_total: str | None = None
    swdkllj_total: str | None = None
    total_due: str | None = None

    def to_api_response(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "supported": self.supported,
            "status": self.status,
            "source": self.source,
            "sourceUrl": self.source_url,
            "message": self.message,
        }
        optional_fields: dict[str, str | None] = {
            "paymentStatus": self.payment_status,
            "registeredPlate": self.registered_plate,
            "ownerName": self.owner_name,
            "ownerAddress": self.owner_address,
            "taxDueDate": self.tax_due_date,
            "stnkExpiryDate": self.stnk_expiry_date,
            "vehicleType": self.vehicle_type,
            "vehicleBrand": self.vehicle_brand,
            "vehicleModel": self.vehicle_model,
            "vehicleYear": self.vehicle_year,
            "vehicleColor": self.vehicle_color,
            "pkbPrincipal": self.pkb_principal,
            "pkbPenalty": self.pkb_penalty,
            "pkbTotal": self.pkb_total,
            "swdklljTotal": self.swdkllj_total,
            "totalDue": self.total_due,
        }
        payload.update({key: value for key, value in optional_fields.items() if value})
        return payload


class SumselTaxLookup:
    def __init__(self, timeout_seconds: float = 8) -> None:
        self.timeout_seconds = timeout_seconds

    def lookup(self, normalized_plate: str) -> dict[str, object]:
        plate_parts = _parse_plate(normalized_plate)
        if plate_parts is None:
            return _unsupported_result("The plate format is not supported for online tax lookup.").to_api_response()

        prefix, number, suffix = plate_parts
        if prefix != "BG":
            return _unsupported_result("Online tax lookup is currently available only for BG plates from South Sumatra.").to_api_response()

        request_body = urlencode({"nopol2": number, "nopol3": suffix, "tekan": ""}).encode("ascii")
        request = Request(
            SUMSEL_TAX_URL,
            data=request_body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "PlatvisionID/0.1 local demo",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                html = response.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError, OSError):
            return TaxLookupResult(
                supported=True,
                status="lookup_failed",
                source=SUMSEL_TAX_SOURCE,
                source_url=SUMSEL_TAX_URL,
                message="The official tax lookup source could not be reached.",
            ).to_api_response()

        return parse_sumsel_tax_response(html).to_api_response()


class OfficialTaxLookup:
    def __init__(self, timeout_seconds: float = 8) -> None:
        self.sumsel_lookup = SumselTaxLookup(timeout_seconds)

    def lookup(self, normalized_plate: str) -> dict[str, object]:
        plate_parts = _parse_plate(normalized_plate)
        if plate_parts is None:
            return _unsupported_result("The plate format is not supported for online tax lookup.").to_api_response()

        prefix, _, _ = plate_parts
        if prefix == "BG":
            return self.sumsel_lookup.lookup(normalized_plate)

        reference_source = REFERENCE_SOURCES_BY_PREFIX.get(prefix)
        if reference_source is None:
            return _unsupported_result("No official online tax lookup adapter is configured for this plate prefix.").to_api_response()

        source, source_url = reference_source
        return TaxLookupResult(
            supported=False,
            status="manual_source_only",
            source=source,
            source_url=source_url,
            message="This region has an official lookup channel, but it requires captcha, an app flow, or extra owner data, so the demo links the source instead of scraping it.",
            registered_plate=normalized_plate.replace(" ", ""),
        ).to_api_response()


def parse_sumsel_tax_response(html: str) -> TaxLookupResult:
    values = _extract_input_values(html)
    registered_plate = _clean_value(values.get("nama_pemilik"))
    owner_name = _clean_value(values.get("nama_wp") or values.get("nama") or values.get("pemilik"))
    owner_address = _clean_value(values.get("alamat_wp") or values.get("alamat"))
    tax_due_date = _clean_value(values.get("tgl_jatuh_tempo"))
    stnk_expiry_date = _clean_value(values.get("tgl_akhir_stnk"))
    vehicle_type = _clean_value(values.get("nm_jenis_kend"))
    vehicle_brand = _clean_value(values.get("nm_merk_kend"))
    vehicle_model = _clean_value(values.get("nm_type_kend"))
    vehicle_year = _clean_value(values.get("thn_buat"))
    vehicle_color = _clean_value(values.get("warna_kend"))
    pkb_principal = _clean_value(values.get("pkb_pokok1") or values.get("pkb1") or values.get("pkb_tunggakan1"))
    pkb_penalty = _clean_value(values.get("pkb_denda1") or values.get("pkb_tunggakan2"))
    pkb_total = _clean_value(values.get("jumlah_pkb") or values.get("pkb_total") or values.get("pkb_tunggakan3"))
    swdkllj_total = _clean_value(values.get("swdkllj_total") or values.get("swdkllj3") or values.get("swdkllj1"))
    total_due = _clean_value(values.get("jumlah") or values.get("jumlah3"))

    found = any(
        [
            owner_name,
            owner_address,
            tax_due_date,
            vehicle_type,
            vehicle_brand,
            vehicle_model,
            vehicle_year,
            total_due and _money_value(total_due) > Decimal("0"),
        ]
    )

    if not found:
        return TaxLookupResult(
            supported=True,
            status="not_found",
            source=SUMSEL_TAX_SOURCE,
            source_url=SUMSEL_TAX_URL,
            message="The official source returned no matching vehicle data.",
            registered_plate=registered_plate,
        )

    return TaxLookupResult(
        supported=True,
        status="found",
        source=SUMSEL_TAX_SOURCE,
        source_url=SUMSEL_TAX_URL,
        message="Vehicle tax data was returned by the official source. Owner name and address were not provided by this source." if not owner_name and not owner_address else "Vehicle tax data was returned by the official source.",
        payment_status=_payment_status(total_due, pkb_penalty),
        registered_plate=registered_plate,
        owner_name=owner_name,
        owner_address=owner_address,
        tax_due_date=tax_due_date,
        stnk_expiry_date=stnk_expiry_date,
        vehicle_type=vehicle_type,
        vehicle_brand=vehicle_brand,
        vehicle_model=vehicle_model,
        vehicle_year=vehicle_year,
        vehicle_color=vehicle_color,
        pkb_principal=pkb_principal,
        pkb_penalty=pkb_penalty,
        pkb_total=pkb_total,
        swdkllj_total=swdkllj_total,
        total_due=total_due,
    )


def _unsupported_result(message: str) -> TaxLookupResult:
    return TaxLookupResult(
        supported=False,
        status="unsupported_region",
        source=SUMSEL_TAX_SOURCE,
        source_url=SUMSEL_TAX_URL,
        message=message,
    )


def _parse_plate(normalized_plate: str) -> tuple[str, str, str] | None:
    match = PLATE_PATTERN.match(normalized_plate.upper())
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3)


def _payment_status(total_due: str | None, pkb_penalty: str | None) -> str:
    if _money_value(pkb_penalty) > Decimal("0"):
        return "overdue_amount"
    if _money_value(total_due) > Decimal("0"):
        return "amount_due"
    return "no_amount_due"


def _money_value(value: str | None) -> Decimal:
    if not value:
        return Decimal("0")
    normalized = value.strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return Decimal("0")


def _clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(unescape(value).split())
    if not cleaned or cleaned in {"-", "0", "0,00"}:
        return None
    return cleaned


def _extract_input_values(html: str) -> dict[str, str]:
    parser = _InputValueParser()
    parser.feed(html)
    return parser.values


class _InputValueParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.values: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "input":
            return
        attr_map = {name.lower(): value or "" for name, value in attrs}
        field_id = attr_map.get("id") or attr_map.get("name")
        if not field_id:
            return
        self.values.setdefault(field_id, attr_map.get("value", ""))
