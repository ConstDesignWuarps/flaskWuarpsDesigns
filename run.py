from mar_tierra import create_app
import os

try:
    ENV = os.environ['ENV']
except:
    ENV = 'DEV'

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000) if ENV == 'PROD' else app.run(host='0.0.0.0', debug=True)

