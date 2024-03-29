from flask import Flask, request, send_file
from PIL import Image
import io
import numpy as np
from osgeo import gdal, gdalnumeric
import os
from matplotlib import cm
# import time
app = Flask(__name__)


@app.route('/<int:zoom>/<int:row>/<int:col>/')
def index(zoom, row, col):
    # start = time.time()
    r = request.args.get('r', default=4, type=int)
    g = request.args.get('g', default=3, type=int)
    b = request.args.get('b', default=2, type=int)
    algo = request.args.get('algo', default='None', type=str)
    img_io = io.BytesIO()
    if algo == 'None':
        img_Arr = np.zeros((256, 256, 4), dtype=np.uint16)
    else:
        img_Arr = np.zeros((256, 256, 2), dtype=np.uint8)
    compress_jpeg = True  # True for auto JPEG
    sent_type = 'image/png'
    # file = f'D:\\EarthEngineCache\\tiles\\S2_SR\\S2B_MSIL2A_20190624T084609_N0212_R107_T35TPF_20190624T123109\\{zoom}\\{row}\\{col}.tif'  # noqa
    file = f'D:\\EarthEngineCache\\tiles\\L8_SR\\Turkey_2019_Mosaic\\{zoom}\\{row}\\{col}.tif'  # noqa
    if os.path.exists(file):
        ds = gdal.Open(file)

        if algo == 'None':
            srcBand = ds.GetRasterBand(r)
            img_Arr[:, :, 0] = gdalnumeric.BandReadAsArray(srcBand)  # noqa
            if r == g:
                if g == b:
                    algo = 'GNone'
                    img_Arr = img_Arr[:, :, :2]
                else:
                    img_Arr[:, :, 1] = img_Arr[:, :, 0]
                    img_Arr[:, :, 2] = gdalnumeric.BandReadAsArray(ds.GetRasterBand(b))  # noqa
            else:
                if r == b:
                    img_Arr[:, :, 2] = img_Arr[:, :, 0]
                else:
                    img_Arr[:, :, 2] = gdalnumeric.BandReadAsArray(ds.GetRasterBand(b))  # noqa
                img_Arr[:, :, 1] = gdalnumeric.BandReadAsArray(ds.GetRasterBand(g))  # noqa

            transparancy = (img_Arr[:, :, 0] != srcBand.GetNoDataValue())  # noqa
            # start = time.time()
            # img_Arr = np.interp(img_Arr, (0, 3000), (0, 255)).astype(np.uint8)  # noqa
            img_Arr = img_Arr * (255/3000)
            img_Arr = img_Arr.clip(0, 255).astype(np.uint8)
            # print("Interpolation Time: ", time.time()-start)
        elif algo == 'NDVI':
            nir = gdalnumeric.BandReadAsArray(ds.GetRasterBand(5))  # 8
            red = gdalnumeric.BandReadAsArray(ds.GetRasterBand(4))
            transparancy = (nir + red) != 0  # noqa
            add_arr = np.add(nir, red, dtype=int)
            sub_arr = np.subtract(nir, red, dtype=int)
            NDVI = np.divide(sub_arr, add_arr, dtype=float)
            # img_Arr[:, :, 0] = np.interp(NDVI, (-1, 1), (0, 255)).astype(np.uint8)  # noqa
            rNDVI = np.interp(NDVI, (-1, 1), (0, 1))  # noqa
            img_Arr = np.uint8(cm.gist_earth(rNDVI)*255)
            img_Arr[:, :, 3] = 0

        elif algo == 'NBR':
            nir = gdalnumeric.BandReadAsArray(ds.GetRasterBand(5))  # 8
            swir = gdalnumeric.BandReadAsArray(ds.GetRasterBand(6))  # 12
            transparancy = (nir + swir) != 0  # noqa
            add_arr = np.add(nir, swir, dtype=int)
            sub_arr = np.subtract(nir, swir, dtype=int)
            NBR = np.divide(sub_arr, add_arr, dtype=float)
            img_Arr[:, :, 0] = np.interp(NBR, (-1, 1), (0, 255)).astype(np.uint8)  # noqa

        compress_jpeg = np.all(transparancy)  # Uncommet for auto JPEG
        # print(compress_jpeg)
        if algo == 'None' or algo == 'NDVI':
            if not compress_jpeg:
                img_Arr[transparancy, 3] = 255
                img = Image.fromarray(img_Arr, 'RGBA')
                # image_save = time.time()
                img.save(img_io, "PNG", compress_level=3)
            else:
                img = Image.fromarray(img_Arr[:, :, :3], 'RGB')
                # image_save = time.time()
                img.save(img_io, "JPEG")
                sent_type = 'image/jpeg'
        else:
            if not compress_jpeg:
                img_Arr[transparancy, 1] = 255
                img = Image.fromarray(img_Arr, 'LA')
                # image_save = time.time()
                img.save(img_io, "PNG", compress_level=3)
            else:
                img = Image.fromarray(img_Arr[:, :, :1].reshape((256, 256)), 'L')  # noqa
                # image_save = time.time()
                img.save(img_io, "JPEG")
                sent_type = 'image/jpeg'

        # end = time.time()
        # print(f"Total Time: {end - start}, Type: {sent_type}")  # noqa
    else:
        return ('', 204)
    img_io.seek(0)
    return send_file(img_io, mimetype=sent_type)


if __name__ == '__main__':
    app.run(debug=False, port=5000)
