"""QR code helper for report patient box."""
import io


def qr_png_bytes(data, border=2):
    """Return PNG bytes for a QR encoding `data`, or None."""
    if not data:
        return None
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_M

        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=border,
        )
        qr.add_data(str(data))
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    except Exception as e:
        print(f'[qr] failed: {e}')
        return None
