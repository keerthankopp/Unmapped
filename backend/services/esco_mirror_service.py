import csv
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _db_path() -> Path:
    return Path(os.getenv("ESCO_MIRROR_DB_PATH", Path(__file__).resolve().parents[1] / "data" / "esco_mirror.sqlite"))


def _connect() -> sqlite3.Connection:
    dbp = _db_path()
    dbp.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(dbp))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS occupations (
              uri TEXT PRIMARY KEY,
              title TEXT,
              description TEXT,
              isco_group TEXT
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS occupations_fts USING fts5(
              uri,
              title,
              description,
              content='occupations',
              content_rowid='rowid'
            );
            CREATE TABLE IF NOT EXISTS occupation_skills (
              occupation_uri TEXT,
              skill_label TEXT,
              is_essential INTEGER,
              PRIMARY KEY (occupation_uri, skill_label)
            );
            """
        )


def _guess_file(files: List[Path], contains_all: List[str]) -> Optional[Path]:
    for p in files:
        name = p.name.lower()
        if all(tok in name for tok in contains_all):
            return p
    return None


def build_from_extracted_csv_folder(folder: str) -> Dict[str, Any]:
    """
    Build a local ESCO mirror sqlite DB from an extracted ESCO CSV download.

    Because ESCO download packages evolve, we detect likely CSV files by filename and columns.
    This builder is intentionally heuristic and will surface explicit errors if it cannot identify files.
    """
    base = Path(folder).resolve()
    if not base.exists():
        raise FileNotFoundError(f"Folder not found: {base}")

    ensure_schema()

    csv_files = [p for p in base.rglob("*.csv")]
    if not csv_files:
        raise RuntimeError("No .csv files found. Make sure you extracted the ESCO CSV zip (use 7-Zip on Windows).")

    occ_file = _guess_file(csv_files, ["occupation"]) or _guess_file(csv_files, ["occupations"])
    rel_file = _guess_file(csv_files, ["occupation", "skill"]) or _guess_file(csv_files, ["occupation", "skill", "relation"])
    skill_file = _guess_file(csv_files, ["skill"]) or _guess_file(csv_files, ["skills"])

    if not occ_file:
        raise RuntimeError("Could not locate an Occupation CSV file in the extracted package.")

    # Load skills label lookup (optional)
    skill_label_by_uri: Dict[str, str] = {}
    if skill_file:
        with skill_file.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            cols = [c.lower() for c in (reader.fieldnames or [])]
            uri_col = next((c for c in reader.fieldnames or [] if c.lower() in ("uri", "concepturi", "id")), None)
            label_col = next(
                (c for c in reader.fieldnames or [] if c.lower() in ("preferredlabel", "title", "label", "prefLabel".lower())),
                None,
            )
            if uri_col and label_col:
                for row in reader:
                    u = (row.get(uri_col) or "").strip()
                    if not u:
                        continue
                    skill_label_by_uri[u] = (row.get(label_col) or "").strip() or u

    # Load occupations
    inserted = 0
    with _connect() as conn, occ_file.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        f_lower = {c.lower(): c for c in fields}

        uri_col = f_lower.get("uri") or f_lower.get("concepturi") or f_lower.get("id")
        title_col = f_lower.get("preferredlabel") or f_lower.get("title") or f_lower.get("label")
        desc_col = f_lower.get("description") or f_lower.get("definition") or f_lower.get("scopenote")
        isco_col = f_lower.get("iscogroup") or f_lower.get("isco") or f_lower.get("isco08") or f_lower.get("isco code")

        if not uri_col or not title_col:
            raise RuntimeError(f"Occupation CSV missing required columns. Found columns: {fields}")

        conn.execute("DELETE FROM occupations")
        conn.execute("DELETE FROM occupations_fts")
        for row in reader:
            uri = (row.get(uri_col) or "").strip()
            if not uri:
                continue
            title = (row.get(title_col) or "").strip()
            desc = (row.get(desc_col) or "").strip() if desc_col else ""
            isco = (row.get(isco_col) or "").strip() if isco_col else ""
            conn.execute(
                "INSERT OR REPLACE INTO occupations(uri, title, description, isco_group) VALUES (?,?,?,?)",
                (uri, title, desc, isco),
            )
            inserted += 1

        # Populate FTS from occupations
        conn.execute(
            "INSERT INTO occupations_fts(rowid, uri, title, description) SELECT rowid, uri, title, description FROM occupations"
        )

    # Load occupation-skill relations (optional but required for readiness)
    rel_inserted = 0
    if rel_file:
        with _connect() as conn, rel_file.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames or []
            f_lower = {c.lower(): c for c in fields}

            occ_col = f_lower.get("occupationuri") or f_lower.get("occupation") or f_lower.get("occupation uri")
            skill_col = f_lower.get("skilluri") or f_lower.get("skill") or f_lower.get("skill uri")
            reltype_col = f_lower.get("relationtype") or f_lower.get("relation type") or f_lower.get("type")
            label_col = f_lower.get("skilllabel") or f_lower.get("skill label")

            if not occ_col or not skill_col:
                # If we can't parse this file, keep mirror usable for search-only.
                rel_file = None
            else:
                conn.execute("DELETE FROM occupation_skills")
                for row in reader:
                    occ_uri = (row.get(occ_col) or "").strip()
                    sk_uri = (row.get(skill_col) or "").strip()
                    if not occ_uri or not sk_uri:
                        continue
                    rel_type = (row.get(reltype_col) or "").strip().lower() if reltype_col else ""
                    is_essential = 1 if "essential" in rel_type else 0
                    label = (row.get(label_col) or "").strip() if label_col else ""
                    if not label:
                        label = skill_label_by_uri.get(sk_uri, sk_uri)
                    conn.execute(
                        "INSERT OR REPLACE INTO occupation_skills(occupation_uri, skill_label, is_essential) VALUES (?,?,?)",
                        (occ_uri, label, is_essential),
                    )
                    rel_inserted += 1

    return {
        "db_path": str(_db_path()),
        "occupations_loaded": inserted,
        "relations_loaded": rel_inserted,
        "occupation_csv": str(occ_file),
        "relation_csv": str(rel_file) if rel_file else None,
        "skill_csv": str(skill_file) if skill_file else None,
        "note": "Local ESCO mirror built from an official ESCO CSV download package.",
    }


def search_occupations_local(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    ensure_schema()
    q = (query or "").strip()
    if not q:
        return []
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT o.uri, o.title, o.isco_group, o.description
            FROM occupations_fts f
            JOIN occupations o ON o.uri = f.uri
            WHERE occupations_fts MATCH ?
            LIMIT ?
            """,
            (q.replace('"', " "), limit),
        ).fetchall()
    return [
        {"uri": r["uri"], "title": r["title"], "iscoGroup": r["isco_group"], "description": r["description"], "source": "ESCO mirror"}
        for r in rows
    ]


def essential_skills_local(occupation_uri: str, limit: int = 50) -> List[str]:
    ensure_schema()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT skill_label
            FROM occupation_skills
            WHERE occupation_uri = ? AND is_essential = 1
            LIMIT ?
            """,
            (occupation_uri, limit),
        ).fetchall()
    return [r["skill_label"] for r in rows]

