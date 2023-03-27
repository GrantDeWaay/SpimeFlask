from io import StringIO, BytesIO

import qrcode
from dotenv import dotenv_values
from flask import send_file

config = dotenv_values("config.env")


def generate_qr_image(crateid):
	img = qrcode.make(config["HOST_URL"] + "/crate/" + crateid)
	img_io = BytesIO()
	img.save(img_io, 'JPEG')
	img_io.seek(0)
	return send_file(img_io, mimetype='image/jpeg')
