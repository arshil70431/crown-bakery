import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'your-secret-key-here'  # change this if you want

    # ABSOLUTE path – works every time
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'crown_bakery.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Razorpay test keys (fill your key ID)
    RAZORPAY_KEY_ID = 'rzp_test_...'       # <-- paste your Key ID here (starts with rzp_test_)
    RAZORPAY_KEY_SECRET = 'your-razorpay-secret-here'   # already filled



    