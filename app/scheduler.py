def scheduler_loop():
    global _last_run

    irrigation_off()  # seguridad al arrancar

    active_irrigation = None
    irrigation_end_time = None

    while True:
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            cur = conn.cursor()

            now = datetime.now()
            now_hm = now.strftime("%H:%M")

            # 1️⃣ Si NO hay riego activo, buscar uno nuevo
            if active_irrigation is None:

                row = cur.execute("""
                    SELECT id, sector, duration
                    FROM irrigation_schedule
                    WHERE start_time = ?
                      AND enabled = 1
                """, (now_hm,)).fetchone()

                if row and _last_run != now_hm:
                    schedule_id, sector, duration = row
                    _last_run = now_hm

                    irrigation_on()  # aquí luego irá zone_on(sector)

                    irrigation_end_time = now + timedelta(minutes=duration)
                    active_irrigation = schedule_id

                    cur.execute("""
                        INSERT INTO irrigation_log (sector, start_time)
                        VALUES (?, ?)
                    """, (sector, now))

                    conn.commit()

            # 2️⃣ Si hay riego activo comprobar si debe finalizar
            if active_irrigation and now >= irrigation_end_time:

                irrigation_off()

                cur.execute("""
                    UPDATE irrigation_log
                    SET end_time = ?
                    WHERE id = (
                        SELECT id FROM irrigation_log
                        ORDER BY id DESC LIMIT 1
                    )
                """, (now,))
                conn.commit()

                active_irrigation = None
                irrigation_end_time = None

            conn.close()

        except Exception as e:
            print("Scheduler error:", e)

        time.sleep(10)  # revisa cada 10 segundos
