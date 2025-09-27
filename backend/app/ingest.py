# backend/app/ingest.py
from __future__ import annotations
import argparse
import asyncio
import os
import pathlib
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import SessionLocal
from app.models.alarm import Alarm

# --- Paramètres globaux ---
TZ_DEFAULT = ZoneInfo(os.getenv("TZ", "Africa/Dakar"))

SEVERITY_MAP = {
    "info": "INFO",
    "minor": "WARN",
    "warn": "WARN",
    "warning": "WARN",
    "major": "MAJOR",
    "critical": "CRITICAL",
}
STATUS_MAP = {
    "open": "OPEN",
    "cleared": "CLEARED",
    "ack": "ACK",
    "acked": "ACK",
    "acknowledged": "ACK",
}

# ---------- Utilitaires DataFrame ----------

def _read_file(path: pathlib.Path) -> pd.DataFrame:
    """Lit CSV/Excel en DataFrame."""
    if path.suffix.lower() in [".xls", ".xlsx", ".xlsm"]:
        return pd.read_excel(path)
    return pd.read_csv(path)

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Uniformise les noms de colonnes (lower/strip)."""
    df = df.copy()
    df.columns = [str(c).lower().strip() for c in df.columns]
    return df

def _pick_first_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Retourne le *nom* de la première colonne existante parmi candidates, sinon None."""
    for name in candidates:
        if name in df.columns:
            return name
    return None

def _combine_first_series(df: pd.DataFrame, *colnames: str) -> pd.Series | None:
    """
    Fusionne plusieurs colonnes par priorité (première non-nulle par ligne).
    Retourne une Series (ou None si aucune colonne).
    """
    cols = [c for c in colnames if c is not None and c in df.columns]
    if not cols:
        return None
    s = df[cols[0]].copy()
    for c in cols[1:]:
        s = s.where(~s.isna(), df[c])  # remplace NaN par valeur de c
    return s

def _parse_dt_column(s: pd.Series | None) -> pd.Series | None:
    """
    Convertit une colonne en datetime. Si naïf, localise Africa/Dakar.
    Laisse None si colonne absente.
    """
    if s is None:
        return None
    # coercition en datetime (gère formats hétérogènes)
    dt = pd.to_datetime(s, errors="coerce", utc=False)
    # dt est une Series de Timestamps (naïfs ou tz-aware)
    # On localise Africa/Dakar si naïf ; si tz-aware, on laisse tel quel.
    # On doit faire cela *élément par élément*.
    def _localize_if_naive(x):
        if pd.isna(x):
            return pd.NaT
        # pandas >= 2 : Timestamp.tzinfo pour savoir si tz-aware
        return x.tz_localize(TZ_DEFAULT) if x.tzinfo is None else x
    return dt.apply(_localize_if_naive)

def _normalize_str_series(s: pd.Series | None, default: str = "") -> pd.Series | None:
    """Transforme en texte, trim, remplace NaN par default."""
    if s is None:
        return None
    s = s.astype("string").fillna(default).str.strip()
    return s

def _map_with_default(s: pd.Series | None, mapping: dict[str, str], default: str) -> pd.Series:
    """Mappe des valeurs textes vers un enum, insensible à la casse ; default si absent/NaN."""
    if s is None:
        return pd.Series([default] * 0)  # sera aligné plus tard si vide
    raw = s.astype("string").str.lower().fillna("")
    return raw.map(mapping).fillna(default)

# ---------- UPSERT ----------

async def _upsert_rows(session: AsyncSession, rows: list[dict], source_file: str | None):
    for i in range(0, len(rows), 1000):
        chunk = rows[i : i + 1000]
        stmt = insert(Alarm).values(chunk)
        stmt = stmt.on_conflict_do_update(
            index_elements=["site_id", "alarm_code", "started_at"],
            set_={
                "site_name": stmt.excluded.site_name,
                "alarm_label": stmt.excluded.alarm_label,
                "severity": stmt.excluded.severity,
                "status": stmt.excluded.status,
                "cleared_at": stmt.excluded.cleared_at,
                "acked_at": stmt.excluded.acked_at,
                "source_file": source_file,
                "updated_at": text("now()"),
            },
        )
        await session.execute(stmt)
    await session.commit()

# ---------- Pipeline principal ----------

async def ingest(path: pathlib.Path, source_file: str | None, truncate: bool):
    df_raw = _read_file(path)
    df = _normalize_columns(df_raw)

    # Colonnes candidates (alias possibles)
    col_site_id   = _pick_first_column(df, ["siteid", "site_id", "site id", "id_site"])
    col_site_name = _pick_first_column(df, ["sitename", "site_name", "site name", "nom_site"])
    # alarm_code: priorité "alarm" puis "alarmcode"
    s_alarm_code  = _combine_first_series(df, _pick_first_column(df, ["alarm"]), _pick_first_column(df, ["alarmcode", "alarm_code"]))
    # alarm_label: priorité "alarmlabel" puis "alarm" puis "alarmcode"
    s_alarm_label = _combine_first_series(
        df,
        _pick_first_column(df, ["alarmlabel", "alarm_label", "alarm label", "libelle_alarme"]),
        _pick_first_column(df, ["alarm"]),
        _pick_first_column(df, ["alarmcode", "alarm_code"]),
    )
    col_severity  = _pick_first_column(df, ["severity", "sev", "criticite"])
    col_status    = _pick_first_column(df, ["status", "state", "etat"])
    col_started   = _pick_first_column(df, ["starttime", "started_at", "start", "debut"])
    col_cleared   = _pick_first_column(df, ["cleartime", "cleared_at", "clear", "fin"])
    col_acked     = _pick_first_column(df, ["acktime", "acked_at", "ack"])

    # Normalisations
    s_site_id   = _normalize_str_series(df[col_site_id])   if col_site_id   else None
    s_site_name = _normalize_str_series(df[col_site_name]) if col_site_name else None

    s_alarm_code  = _normalize_str_series(s_alarm_code)    # peut être None si introuvable
    s_alarm_label = _normalize_str_series(s_alarm_label)   # idem

    s_severity = _map_with_default(df[col_severity] if col_severity else None, SEVERITY_MAP, "INFO")
    s_status   = _map_with_default(df[col_status]   if col_status   else None, STATUS_MAP, "OPEN")

    s_started  = _parse_dt_column(df[col_started]) if col_started else None
    s_cleared  = _parse_dt_column(df[col_cleared]) if col_cleared else None
    s_acked    = _parse_dt_column(df[col_acked])   if col_acked   else None

    # Longueur cible (nb de lignes)
    n = len(df)

    # Valeurs par défaut si colonnes manquantes
    if s_site_id is None:    s_site_id = pd.Series([""] * n, dtype="string")
    if s_site_name is None:  s_site_name = pd.Series([""] * n, dtype="string")
    if s_alarm_code is None: s_alarm_code = pd.Series([""] * n, dtype="string")
    if s_alarm_label is None:
        # fallback final = alarm_code
        s_alarm_label = s_alarm_code.copy()

    if s_started is None: s_started = pd.Series([pd.NaT] * n, dtype="datetime64[ns, UTC]").astype("datetime64[ns]")
    # cleared/acked peuvent rester None/NaT
    if s_cleared is None: s_cleared = pd.Series([pd.NaT] * n, dtype="datetime64[ns]").astype("datetime64[ns]")
    if s_acked   is None: s_acked   = pd.Series([pd.NaT] * n, dtype="datetime64[ns]").astype("datetime64[ns]")

    # Construction DataFrame final pour export “records”
    out = pd.DataFrame({
        "site_id": s_site_id,
        "site_name": s_site_name,
        "alarm_code": s_alarm_code,
        "alarm_label": s_alarm_label,
        "severity": s_severity.reindex(range(n), fill_value="INFO"),
        "status":   s_status.reindex(range(n),   fill_value="OPEN"),
        "started_at": s_started,
        "cleared_at": s_cleared,
        "acked_at":   s_acked,
    })

    # Nettoyage basique (suppression des lignes sans alarm_code ou sans site_id)
    out = out[(out["alarm_code"].astype("string").str.len() > 0) & (out["site_id"].astype("string").str.len() > 0)]
    if out.empty:
        print("Aucune ligne exploitable après normalisation (site_id/alarm_code manquants).")
        return

    # Conversion en records
    rows: list[dict] = out.assign(source_file=source_file, extras=None).to_dict(orient="records")

    # Exécution DB
    async with SessionLocal() as session:
        if truncate:
            await session.execute(text("TRUNCATE TABLE alarms RESTART IDENTITY"))
            await session.commit()
        await _upsert_rows(session, rows, source_file)

# ---------- CLI ----------

def main():
    parser = argparse.ArgumentParser(description="Ingestion RTMC → alarms")
    parser.add_argument("path", type=str, help="Chemin vers CSV/Excel RTMC")
    parser.add_argument("--source-file", type=str, default=None, help="Étiquette de traçabilité")
    parser.add_argument("--truncate", action="store_true", help="TRUNCATE avant import")
    args = parser.parse_args()

    p = pathlib.Path(args.path)
    if not p.exists():
        raise SystemExit(f"Fichier introuvable: {p}")

    asyncio.run(ingest(p, args.source_file, args.truncate))

if __name__ == "__main__":
    main()
