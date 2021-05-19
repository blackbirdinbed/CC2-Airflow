from flask import Flask, jsonify
from servicev1 import Service

service = Service()
app = Flask(__name__)

# -------- API routes for forecasting -------- #

# Prediction
@app.route('/servicio/v1/prediccion/<n>horas', methods = ['GET'])
def inicio(n):
	if int(n) == 24 or int(n) == 48 or int(n) == 72:
		return jsonify(service.predict(n)), 200
	else:
		return jsonify(status="Error", api_route="/servicio/v1/prediccion/<n>horas", msg="Valores de n deben ser 24, 48 o 72"), 400

# Ruta para ver las rutas
@app.route('/', methods = ['GET'])
def index():
	return jsonify(status="OK", api_route="/servicio/v1/prediccion/<n>horas", msg="El servicio"), 200

if __name__ == '__main__':
	app.run(host='localhost', debug=True)
