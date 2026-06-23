# from streamlit.testing.v1 import AppTest

# def test_app_loads():

#     app = AppTest.from_file("inventory.py")

#     app.run()

#     assert app.exception is None
from streamlit.testing.v1 import AppTest

def test_app_loads():
    app = AppTest.from_file("inventory.py").run()

    assert len(app.exception) == 0