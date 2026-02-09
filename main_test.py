from main import morning, start_station, prepare

def test_morning():
    morning()

def test_station():
    prepare(0, True)
    start_station()

def main():
    test_morning()
    test_station()

if __name__ == "__main__":
    main()