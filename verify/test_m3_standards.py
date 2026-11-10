"""M3 - Kendi custom mode'um: Mode + Rules + Skill (.bob/)."""

import re
from pathlib import Path

import pytest
import yaml
from common import ROOT

BOB = ROOT / ".bob"
VALID_GROUPS = {"read", "edit", "execute", "mcp", "skill", "todo", "subagent", "mode"}


def _mentions(text: str, *alternatives: str) -> bool:
    lowered = text.lower()
    return any(alt.lower() in lowered for alt in alternatives)


def _rules_text() -> str:
    """Kurallar .bob/rules/ (tum modlar) veya .bob/rules-<mod-slug>/ (yalniz o mod) altinda olabilir."""
    files = sorted(
        p
        for d in [BOB / "rules", *BOB.glob("rules-*")]
        for p in d.glob("*")
        if p.is_file() and p.suffix in (".md", ".txt")
    )
    assert files, ".bob/rules/ veya .bob/rules-<mod-slug>/ altinda kural dosyasi (.md) yok"
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in files)


# ---- Rules ---------------------------------------------------------------


def test_rules_file_exists_with_substance():
    """.bob/rules/ altinda anlamli bir kural dosyasi var"""
    text = _rules_text()
    assert len(text.strip()) >= 300, f"kurallar cok kisa ({len(text.strip())} karakter); handbook'u ozetleyin"


def test_rules_cover_money_standard():
    """Kurallar para standardini soyluyor (Decimal, float yok)"""
    text = _rules_text()
    assert _mentions(text, "decimal"), "kurallarda 'Decimal' gecmiyor"
    assert _mentions(text, "float"), "kurallar float kullanimini acikca yasaklamali"


def test_rules_cover_error_envelope():
    """Kurallar hata zarfini tanimliyor ({'error': {'code', 'message'}})"""
    text = _rules_text()
    assert _mentions(text, '"error"', "'error'", "hata zarf", "error envelope"), "hata zarfi anlatilmiyor"
    assert _mentions(text, "code"), "zarf icindeki 'code' alani anlatilmiyor"


def test_rules_cover_pii_logging():
    """Kurallar log'a kisisel veri (PII) yazmayi yasakliyor"""
    text = _rules_text()
    assert _mentions(text, "pii", "kisisel veri", "kişisel veri"), "PII kurali yok"
    assert _mentions(text, "log"), "loglama kurali yok"


def test_rules_cover_security_basics():
    """Kurallar gizli bilgi ve parametreli SQL konusunu iceriyor"""
    text = _rules_text()
    assert _mentions(text, "secret", "gizli", "parola", "password"), "gizli bilgi kurali yok"
    assert _mentions(text, "parametre", "parameteriz", "parameteris"), "parametreli SQL kurali yok"


# ---- Skill ---------------------------------------------------------------


def _skills():
    return sorted(p for p in (BOB / "skills").glob("*/SKILL.md"))


def test_skill_exists_and_name_is_valid():
    """.bob/skills/<ad>/SKILL.md var ve klasor adi gecerli (kucuk harf-tire)"""
    skills = _skills()
    assert skills, ".bob/skills/<skill-adi>/SKILL.md bulunamadi"
    bad = [s.parent.name for s in skills if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s.parent.name) or len(s.parent.name) > 64]
    assert not bad, f"gecersiz skill klasor adi (sessizce atlanir!): {bad}"


def _frontmatter(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    assert match, f"{path.parent.name}/SKILL.md: '---' ile baslayan frontmatter yok"
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def test_skill_frontmatter_is_complete():
    """Skill frontmatter'i: name klasorle ayni, description tetikleyici"""
    assert _skills(), "skill yok"
    for skill in _skills():
        meta, _ = _frontmatter(skill)
        assert meta.get("name") == skill.parent.name, f"frontmatter 'name' ({meta.get('name')!r}) klasor adiyla ({skill.parent.name!r}) ayni olmali"
        desc = str(meta.get("description", ""))
        assert len(desc) >= 40, "description cok kisa; Bob'un ne zaman devreye alacagini anlatmali"
        assert _mentions(desc, "use when", "kullan", "when"), "description bir tetikleyici ifade icermeli ('Use when ...')"


def test_skill_body_encodes_test_standard():
    """Skill govdesi test standardini tarif ediyor (TestClient, reset, sinir degeri)"""
    bodies = "\n".join(_frontmatter(s)[1] for s in _skills())
    assert len(bodies.strip()) >= 300, "skill govdesi cok kisa"
    assert _mentions(bodies, "testclient"), "TestClient gecmiyor"
    assert _mentions(bodies, "reset"), "store.reset() adimi yok"
    assert _mentions(bodies, "boundary", "sinir", "sınır"), "sinir degeri testi yok"
    assert _mentions(bodies, "happy", "mutlu"), "mutlu yol yok"
    assert _mentions(bodies, "negative", "negatif"), "negatif durum yok"


# ---- Custom mode ---------------------------------------------------------


def _modes():
    path = BOB / "custom_modes.yaml"
    assert path.exists(), ".bob/custom_modes.yaml yok (proje modlari burada tanimlanir)"
    raw = path.read_text(encoding="utf-8")
    assert all(ord(c) < 128 for c in raw), "dosyada ASCII disi karakter var (kivrik tirnak, uzun tire...) - yukleyici bunlari temizler, sade ASCII kullanin"
    data = yaml.safe_load(raw) or {}
    modes = data.get("customModes")
    assert isinstance(modes, list) and modes, "'customModes' listesi bos veya yok"
    return modes


def _custom_mode():
    for mode in _modes():
        if mode.get("slug") not in ("agent", "plan", "ask"):
            return mode
    pytest.fail("yeni bir mod tanimlanmamis", pytrace=False)


def test_mode_schema_is_valid():
    """Mod semasi gecerli (slug, name, roleDefinition, benzersiz slug)"""
    modes = _modes()
    slugs = [m.get("slug") for m in modes]
    assert len(slugs) == len(set(slugs)), "tekrar eden slug: tum dosya yuklenmez"
    mode = _custom_mode()
    assert re.fullmatch(r"[a-zA-Z0-9-]+", str(mode.get("slug", ""))), f"gecersiz slug: {mode.get('slug')!r}"
    assert mode.get("name"), "mod icin 'name' gerekli"
    assert len(str(mode.get("roleDefinition", ""))) >= 80, "roleDefinition en az 80 karakter, odakli bir persona olmali"


def _group_names(mode):
    names = []
    for group in mode.get("groups", []):
        names.append(group[0] if isinstance(group, list) else group)
    return names


def test_mode_groups_are_real_and_explicit():
    """Mod yetki gruplari gercek isimler (command/write gibi sessiz hatalar yok)"""
    mode = _custom_mode()
    names = _group_names(mode)
    assert names, "groups bos: mod hicbir arac kullanamaz"
    unknown = [n for n in names if n not in VALID_GROUPS]
    assert not unknown, f"taninmayan grup (sessizce hicbir sey vermez): {unknown}. Gecerli: {sorted(VALID_GROUPS)}"
    assert len(names) == len(set(names)), "grup adi tekrar ediyor: dosya yuklenmez"
    assert "read" in names and "execute" in names, "QA modu dosyalari okuyabilmeli ve testleri calistirabilmeli (read + execute)"


def test_mode_edit_is_restricted_to_tests():
    """Mod yalnizca tests/ altindaki dosyalari duzenleyebilir (fileRegex)"""
    mode = _custom_mode()
    edit = next((g for g in mode.get("groups", []) if isinstance(g, list) and g[0] == "edit"), None)
    assert edit is not None, "'edit' grubu fileRegex kisitiyla tanimlanmali (tuple bicimi: - - edit / - fileRegex: ...)"
    regex = (edit[1] or {}).get("fileRegex")
    assert regex, "edit grubunda fileRegex yok; mod her dosyayi degistirebilir"
    try:
        pattern = re.compile(regex)
    except re.error as exc:
        pytest.fail(f"fileRegex derlenemiyor (dosyanin tamami atilir): {exc}", pytrace=False)
    assert pattern.search("tests/test_transfers.py"), "fileRegex test dosyalarini kapsamiyor (tests/test_transfers.py)"
    for forbidden in ("services/core/main.py", "services/core/fees.py", "deploy/Dockerfile"):
        assert not pattern.search(forbidden), f"fileRegex '{forbidden}' dosyasina da izin veriyor"
