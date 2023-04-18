from flask import Flask, request, render_template

from DB import DB
from enums import OPS
from qrcode_generate import generate_qr_image

app = Flask(__name__)


@app.route("/crate/<crateid>")
def consumer_view(crateid):
	return render_template('crate_history.html', id=crateid, history=DB().execute(OPS.GET_TRANSACTIONS, crateid),
							   image="/api/qr/" + crateid)


@app.route("/api/crate", methods=['POST', 'GET'])
def crate():
	if request.method == 'POST':
		return DB().execute(OPS.POST_CRATE, request.form)
	elif request.method == 'GET':
		return DB().execute(OPS.GET_CRATE, request.form)
	return 404


@app.route("/api/location", methods=['POST', 'GET'])
def location():
	if request.method == 'POST':
		return DB().execute(OPS.POST_LOCATION, request.form)
	elif request.method == 'GET':
		return DB().execute(OPS.GET_LOCATION, request.form)
	return 404


@app.route("/api/delete/all_transactions", methods=['POST'])
def delete_all():
	return DB().execute(OPS.DELETE_ALL_TRANSACTIONS, request.form["ADMIN-CODE"])


@app.route("/api/transaction", methods=['POST'])
def post_transaction():
	if request.method == 'POST':
		return DB().execute(OPS.POST_TRANSACTION, request.form)
	return 404


@app.route("/api/qr/<crateid>", methods=['GET'])
def gen_qr(crateid):
	return generate_qr_image(crateid)


@app.route("/api/transactions/<crateid>", methods=['GET'])
def get_transactions(crateid):
	return DB().execute(OPS.GET_TRANSACTIONS, crateid), 200


# Removed functionality, it won't be ready or necessary for the demo
#
# @app.route("/api/location/connection", methods=['POST', 'GET'])
# def location_links():
# 	if request.method == 'POST':
# 		return DB().execute(OPS.POST_APPROVED_CONNECTION, request.form)
# 	elif request.method == 'GET':
# 		return DB().execute(OPS.GET_APPROVED_CONNECTIONS, request.form)
# 	return 404

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
