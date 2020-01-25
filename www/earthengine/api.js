var map;
var r_selected = 4;
var g_selected = 3;
var b_selected = 2;
var algo_selected = 'None';
function init() {
    document.removeEventListener('DOMContentLoaded', init);
    const projection = ol.proj.get('EPSG:4326');
    const projectionExtent = projection.getExtent();
    const size = ol.extent.getWidth(projectionExtent) / 256;
    const resolutions = new Array(14);
    const matrixIds = new Array(14);
    var scaleview = new ol.control.ScaleLine({
        units: 'metric'
    });
    // create matrix
    for (let z = 0; z < 14; ++z) {
        // generate resolutions and matrixIds arrays for this WMTS
        // eslint-disable-next-line no-restricted-properties
        resolutions[z] = size / Math.pow(2, (z + 1));
        matrixIds[z] = z;
    }
    var wmslayer_s2 = new ol.layer.Tile({
        source: new ol.source.WMTS({
        url: 'http://127.0.0.1:5000/{TileMatrix}/{TileRow}/{TileCol}/?r=4&g=3&b=2',
        projection,
        tileGrid: new ol.tilegrid.WMTS({
            origin: ol.extent.getTopLeft(projectionExtent),
            resolutions:resolutions,//slice(0,-1)
            matrixIds:matrixIds,//slice(0,-1)
        }),
        requestEncoding: 'REST',
        transition: 0,
		wrapX:!0,
        })
    });
    var tile_grid = new ol.tilegrid.WMTS({origin:ol.extent.getTopLeft(projectionExtent),resolutions:resolutions,matrixIds:matrixIds});
        var s2maps = new ol.layer.Tile({
        source: new ol.source.WMTS({
            layer:'s2cloudless',
            matrixSet:'WGS84',
            format:'image/jpeg',
            projection:projection,
            tileGrid:tile_grid,
            style:'default',
            wrapX:!0,
            urls:[
            "//a.s2maps-tiles.eu/wmts/",
            "//b.s2maps-tiles.eu/wmts/",
            "//c.s2maps-tiles.eu/wmts/",
            "//d.s2maps-tiles.eu/wmts/",
            "//e.s2maps-tiles.eu/wmts/"
            ]
        })
        });
    map = new ol.Map({
        target: 's2map',
        layers: [
            s2maps,
            wmslayer_s2,
        ],
        view: new ol.View({
            projection,
            center: [29, 41],
            zoom: 12,
            maxZoom: 17,
            minZoom: 3
        }),
        controls: ol.control.defaults({
            attributionOptions: {
                collapsible: false
            },
        }),
    });
    map.addControl(scaleview);
    $('select').on('change', function(e){
        if(this.id === 'redSelect')
            r_selected = this.value.substr(1);
        else if(this.id === 'greenSelect')
            g_selected = this.value.substr(1);
        else if(this.id === 'blueSelect')
            b_selected = this.value.substr(1);
        else if(this.id === 'algoSelect')
            algo_selected = this.value;
        map.getLayers().item(1).getSource().setUrl("http://127.0.0.1:5000/{TileMatrix}/{TileRow}/{TileCol}/?r="+r_selected+"&g="+g_selected+"&b="+b_selected+"&algo="+algo_selected);
    });
}
document.addEventListener('DOMContentLoaded', init);