"""Barcode rendering for sample labels."""
import io
from barcode import Code128
from barcode.writer import ImageWriter


class _NoTextWriter(ImageWriter):
    """ImageWriter that draws the barcode bars only — no human-readable text."""
    def _paint_text(self, xpos, ypos):
        return


def code128_png(data, module_height=8.0, module_width=0.25, quiet_zone=1.5):
    """Return a BytesIO with a Code-128 PNG (bars only, no text)."""
    buf = io.BytesIO()
    writer = _NoTextWriter()
    writer.set_options({
        'module_height': module_height,
        'module_width': module_width,
        'quiet_zone': quiet_zone,
        'background': 'white',
        'foreground': 'black',
        'write_text': False,
    })
    barcode = Code128(str(data), writer=writer)
    barcode.write(buf)
    buf.seek(0)

    # Crop the PNG to remove any extra whitespace at bottom
    try:
        from PIL import Image as _PILImage
        import io as _io
        _img = _PILImage.open(buf).convert('RGB')
        # Find bounding box of non-white content
        _bg = _PILImage.new('RGB', _img.size, (255, 255, 255))
        _diff = _PILImage.eval(_img, lambda p: 0)  # placeholder
        # Simpler: crop by thresholding
        _gray = _img.convert('L')
        _bbox = _gray.point(lambda x: 0 if x > 200 else 255).getbbox()
        if _bbox:
            _img = _img.crop(_bbox)
        _out = _io.BytesIO()
        _img.save(_out, format='PNG')
        _out.seek(0)
        return _out
    except Exception:
        buf.seek(0)
        return buf


def sample_suffix(idx):
    """A, B, C, ... Z, AA, AB, ... for item labels."""
    letters = ''
    n = idx
    while True:
        letters = chr(65 + (n % 26)) + letters
        n = n // 26 - 1
        if n < 0:
            break
    return letters
