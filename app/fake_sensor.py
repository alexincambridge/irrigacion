import random

def read_fake_sensors():
    return {
        "temperature": round(random.uniform(18,32),1),
        "humidity": round(random.uniform(40,80),1),
        "solar": round(random.uniform(0,1000),0),
        "pressure": round(random.uniform(980,1030),1),
        "ec": round(random.uniform(1.2,3.5),2),
        "ph": round(random.uniform(5.5,7.2),2)
    }
