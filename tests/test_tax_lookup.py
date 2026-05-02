from platvision_id.modules.alpr.tax_lookup import OfficialTaxLookup, SumselTaxLookup, parse_sumsel_tax_response


def test_sumsel_tax_parser_extracts_vehicle_and_amounts_without_mislabeling_plate_as_owner() -> None:
    html = """
    <html>
      <input id="nama_pemilik" value="BG1352AE">
      <input id="alamat2" value="">
      <input id="tgl_jatuh_tempo" value="01-09-2026">
      <input id="tgl_akhir_stnk" value="01-09-2028">
      <input id="nm_jenis_kend" value="MINIBUS">
      <input id="nm_merk_kend" value="TOYOTA">
      <input id="nm_type_kend" value="INNOVA">
      <input id="thn_buat" value="2021">
      <input id="warna_kend" value="PUTIH">
      <input id="pkb1" value="2.000.000,00">
      <input id="pkb_tunggakan2" value="100.000,00">
      <input id="pkb_tunggakan3" value="2.100.000,00">
      <input id="swdkllj1" value="143.000,00">
      <input id="jumlah" value="2.243.000,00">
    </html>
    """

    payload = parse_sumsel_tax_response(html).to_api_response()

    assert payload["status"] == "found"
    assert payload["paymentStatus"] == "overdue_amount"
    assert payload["registeredPlate"] == "BG1352AE"
    assert "ownerName" not in payload
    assert "ownerAddress" not in payload
    assert payload["vehicleBrand"] == "TOYOTA"
    assert payload["totalDue"] == "2.243.000,00"


def test_sumsel_tax_parser_returns_not_found_for_empty_response() -> None:
    payload = parse_sumsel_tax_response('<input id="pkb_tunggakan1" value="0,00">').to_api_response()

    assert payload["status"] == "not_found"
    assert "ownerName" not in payload


def test_sumsel_tax_parser_keeps_first_value_for_duplicate_source_ids() -> None:
    html = """
    <input id="nama_pemilik" value="BG1352AE">
    <input id="thn_buat" value="2014">
    <input id="thn_buat" value="BENSIN">
    <input id="thn_buat" value="PUTIH">
    <input id="nm_jenis_kend" value="MINIBUS">
    """

    payload = parse_sumsel_tax_response(html).to_api_response()

    assert payload["vehicleYear"] == "2014"


def test_sumsel_tax_lookup_rejects_non_bg_plate_without_network() -> None:
    payload = SumselTaxLookup().lookup("B 2156 TOR")

    assert payload["status"] == "unsupported_region"
    assert payload["supported"] is False


def test_official_tax_lookup_returns_manual_source_for_jabar_plate_without_scraping_captcha() -> None:
    payload = OfficialTaxLookup().lookup("D 1234 ABC")

    assert payload["status"] == "manual_source_only"
    assert payload["source"] == "Bapenda Jawa Barat"
    assert payload["sourceUrl"] == "https://bapenda.jabarprov.go.id/infopkb/"
