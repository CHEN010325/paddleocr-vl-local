import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def compose_service_block(compose: str, service: str) -> str:
    match = re.search(
        rf"^  {re.escape(service)}:\s*\n(?P<body>.*?)(?=^  [A-Za-z0-9][A-Za-z0-9_-]*:\s*\n|\Z)",
        compose,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing Compose service: {service}"
    return match.group("body")


def test_source_mounted_web_services_receive_the_exporter_module_read_only():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    for service in ("pandocr-controller", "pandocr-web"):
        block = compose_service_block(compose, service)
        assert block.count("./exporters.py:/app/exporters.py:ro") == 1


def test_navidc_backend_environment_belongs_to_the_navidc_service():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    hpd = compose_service_block(compose, "hpd-parsing-api")
    navidc = compose_service_block(compose, "navidc-ocr-api")

    assert "NAVIDC_OCR_" not in hpd
    assert "NAVIDC_OCR_BACKEND=${NAVIDC_OCR_BACKEND:-vllm-async-engine}" in navidc


def test_navidc_is_included_in_release_image_matrix_and_overlay():
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    release_compose = (ROOT / "docker-compose.release.yml").read_text(encoding="utf-8")

    assert "name: navidc-ocr" in workflow
    assert "dockerfile: Dockerfile.navidc-ocr" in workflow
    navidc = compose_service_block(release_compose, "navidc-ocr-api")
    assert "ghcr.io/chen010325/paddleocr-local-navidc-ocr:${PANDOCR_IMAGE_TAG:-latest}" in navidc
