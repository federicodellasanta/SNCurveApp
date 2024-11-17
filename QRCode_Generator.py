import qrcode

# The URL of your Streamlit app
url = "https://sncurveapp.streamlit.app/"

# Create the QR code
qr = qrcode.QRCode(
    version=1,  # controls the size of the QR code (1 is the smallest)
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # controls error correction (L is low)
    box_size=10,  # size of each box in the QR code grid
    border=4,  # thickness of the border around the QR code
)

qr.add_data(url)  # Add your URL data
qr.make(fit=True)  # Ensure the QR code is sized correctly

# Create an image from the QR code
img = qr.make_image(fill='black', back_color='white')

# Save or display the image
img.save("sn_curve_app_qr.png")

# Optionally display the image (for testing purposes)
img.show()
