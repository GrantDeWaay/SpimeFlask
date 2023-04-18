from io import BytesIO

import qrcode
from flask import send_file, request


def generate_qr_image(crateid):
	img = qrcode.make(request.host_url + "/crate/" + crateid)
	img_io = BytesIO()
	img.save(img_io, 'JPEG')
	img_io.seek(0)
	return send_file(img_io, mimetype='image/jpeg')
