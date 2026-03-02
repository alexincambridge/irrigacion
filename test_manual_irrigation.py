#!/usr/bin/env python3
"""
Test script to verify manual irrigation logic
Simulates what happens when a manual irrigation is active
"""

import sqlite3
from datetime import datetime

DB_PATH = "instance/irrigation.db"

def test_manual_irrigation_logic():
    """Test the scheduler logic for manual irrigation"""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    print("=" * 60)
    print("PRUEBA: Lógica de Riego Manual")
    print("=" * 60)

    # Simulate sector 1 with manual irrigation in progress
    sector = 1

    print(f"\n1. Buscando riegos programados para sector {sector}...")
    active_schedules = cur.execute("""
        SELECT id, sector, start_time, end_time, duration_minutes
        FROM irrigation_schedule
        WHERE date = date('now')
          AND enabled = 1
          AND start_time <= strftime('%H:%M', 'now')
          AND end_time > strftime('%H:%M', 'now')
    """).fetchall()

    print(f"   Riegos programados: {len(active_schedules)}")
    for row in active_schedules:
        print(f"   - Sector {row['sector']}: {row['start_time']} a {row['end_time']}")

    # Check for manual irrigation
    print(f"\n2. Buscando riegos manuales activos para sector {sector}...")
    manual_active = cur.execute("""
        SELECT id, start_time FROM irrigation_log
        WHERE sector = ?
          AND type = 'manual'
          AND end_time IS NULL
        ORDER BY id DESC
        LIMIT 1
    """, (sector,)).fetchone()

    if manual_active:
        print(f"   ✓ Hay riego manual ACTIVO")
        print(f"   - Iniciado: {manual_active['start_time']}")
        print(f"   - Estado: EN CURSO")
    else:
        print(f"   ✗ No hay riego manual activo")

    # Determine if zone should stay on
    sector_in_schedule = any(row['sector'] == sector for row in active_schedules)

    print(f"\n3. Decisión del scheduler:")
    print(f"   - Sector en riegos programados: {sector_in_schedule}")
    print(f"   - Sector en riegos manuales: {bool(manual_active)}")

    if sector_in_schedule:
        print(f"   → ZONA DEBE ESTAR ENCENDIDA (riego programado)")
    elif manual_active:
        print(f"   → ZONA DEBE ESTAR ENCENDIDA (riego manual activo)")
    else:
        print(f"   → ZONA DEBE ESTAR APAGADA (no hay riego)")

    print("\n" + "=" * 60)
    print("✓ Prueba completada")
    print("=" * 60)

    conn.close()

if __name__ == "__main__":
    test_manual_irrigation_logic()

