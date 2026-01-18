from app.fake_sensors import read_fake_sensors

data = read_fake_sensors()

db.execute("""
INSERT INTO sensor_data
(temperature, humidity, solar, pressure, ec, ph)
VALUES (?,?,?,?,?,?)
""", (
  data["temperature"],
  data["humidity"],
  data["solar"],
  data["pressure"],
  data["ec"],
  data["ph"]
))
