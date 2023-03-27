from flask import Flask, request, render_template

from DB import DB
from enums import OPS
from qrcode_generate import generate_qr_image

app = Flask(__name__)


@app.route("/crate/<crateid>")
def consumer_view(crateid):
	return render_template('/crate_history.html', id=crateid, history=DB().execute(OPS.GET_TRANSACTIONS, crateid))


@app.route("/api/crate", methods=['POST', 'GET'])
def crate():
	if request.method == 'POST':
		return DB().execute(OPS.POST_CRATE, request.form['locid'])
	elif request.method == 'GET':
		return DB().execute(OPS.GET_CRATE, request.form['crateid'])
	return 404


@app.route("/api/location", methods=['POST', 'GET'])
def location():
	if request.method == 'POST':
		return DB().execute(OPS.POST_LOCATION)
	elif request.method == 'GET':
		return DB().execute(OPS.GET_LOCATION, request.form['locid'])
	return 404


@app.route("/api/delete/all")
def delete_all():
	return DB().execute(OPS.DELETE_ALL)


@app.route("/api/transaction", methods=['POST'])
def post_transaction():
	if request.method == 'POST':
		return DB().execute(OPS.POST_TRANSACTION, [request.form['crateid'], request.form['locid']])
	return 404

@app.route("/qr/<crateid>")
def gen_qr(crateid):
	return generate_qr_image(crateid)

#bc310940-4b27-4a3a-bfe1-9d1d30ec06f6

@app.route("/api/transactions/<crateid>")
def get_trans(crateid):
	return DB().execute(OPS.GET_TRANSACTIONS, crateid),200
if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000)
