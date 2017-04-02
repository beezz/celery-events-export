from event_generator import app

@app.task
def add(a, b):
    print("Result: {}".format(a + b))
    return a + b
