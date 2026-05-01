from __future__ import annotations

from .domain import RegionInfo


REGION_BY_PREFIX = {
    "A": "Banten: Serang, Cilegon, Pandeglang, Lebak, Tangerang area",
    "B": "DKI Jakarta, Depok, Tangerang, and Bekasi",
    "D": "Bandung Raya",
    "E": "Cirebon, Indramayu, Majalengka, and Kuningan",
    "F": "Bogor, Sukabumi, and Cianjur",
    "T": "Karawang, Purwakarta, and Subang",
    "Z": "Garut, Tasikmalaya, Ciamis, Banjar, and Pangandaran",
    "G": "Pekalongan, Tegal, Brebes, Pemalang, and Batang",
    "H": "Semarang, Salatiga, Kendal, and Demak",
    "K": "Pati, Kudus, Jepara, Rembang, Blora, and Grobogan",
    "R": "Banyumas, Cilacap, Purbalingga, and Banjarnegara",
    "AA": "Kedu area: Magelang, Purworejo, Kebumen, Temanggung, and Wonosobo",
    "AB": "Yogyakarta Special Region",
    "AD": "Surakarta area",
    "AE": "Madiun, Ngawi, Magetan, Ponorogo, and Pacitan",
    "AG": "Kediri, Blitar, Tulungagung, Trenggalek, and Nganjuk",
    "L": "Surabaya",
    "M": "Madura",
    "N": "Malang, Pasuruan, Probolinggo, Lumajang, and Batu",
    "P": "Jember, Banyuwangi, Bondowoso, and Situbondo",
    "S": "Bojonegoro, Tuban, Lamongan, Jombang, and Mojokerto",
    "W": "Sidoarjo and Gresik",
    "DK": "Bali",
    "DR": "Lombok, Mataram, and West Nusa Tenggara area",
    "EA": "Sumbawa area",
    "EB": "Flores area",
    "ED": "Sumba area",
    "KB": "West Kalimantan",
    "DA": "South Kalimantan",
    "KH": "Central Kalimantan",
    "KT": "East Kalimantan",
    "KU": "North Kalimantan",
    "DB": "North Sulawesi",
    "DL": "Sangihe, Talaud, and Sitaro",
    "DM": "Gorontalo",
    "DN": "Central Sulawesi",
    "DT": "Southeast Sulawesi",
    "DD": "South Sulawesi",
    "DC": "West Sulawesi",
    "DE": "Maluku",
    "DG": "North Maluku",
    "PA": "Papua",
    "PB": "West Papua",
    "BH": "Jambi",
    "BG": "South Sumatra",
    "BA": "West Sumatra",
    "BE": "Lampung",
    "BD": "Bengkulu",
    "BB": "North Sumatra west coast area",
    "BK": "North Sumatra east coast area",
    "BM": "Riau",
    "BP": "Riau Islands",
    "BN": "Bangka Belitung",
    "BL": "Aceh",
}


def lookup_region(prefix: str | None) -> RegionInfo:
    if not prefix:
        return RegionInfo(code=None, name="Unknown region")
    normalized_prefix = prefix.upper()
    return RegionInfo(
        code=normalized_prefix,
        name=REGION_BY_PREFIX.get(normalized_prefix, "Unknown region"),
    )
