from bs4 import BeautifulSoup
import requests
from flask import Flask, json, request, jsonify
from flask_caching import Cache
from flask_cors import CORS
from flask_compress import Compress

app = Flask(__name__)
CORS(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
Compress(app)

# Önbellekleme yapılandırması
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

URL = "https://borsa.doviz.com/hisseler"
hisse_list = []

def hisse_temel(page=1, limit=20):
    hisse_list.clear()
    result = requests.get(URL)
    doc = BeautifulSoup(result.text, "html.parser")
    tbody = doc.tbody
    trs = tbody.find_all("tr")

    for tr in trs:
        td_list = tr.find_all("td")[1:7]
        if len(td_list) == 6:
            anlik, yuksek, dusuk, hacim, degisim, saat = td_list
            hisse_adi = tr['data-name'].split('-')
            icon = tr.find('img')['src']
            hisse = {
                "Hisse Adi": hisse_adi[1],
                "Hisse_Kodu": hisse_adi[0],
                "Anlik fiyat": anlik.text.strip(),
                "Yuksek": yuksek.text.strip(),
                "Dusuk": dusuk.text.strip(),
                "Hacim": hacim.text.strip(),
                "Degisim": degisim.text.strip(),
                "Saat": saat.text.strip(),
                "Icon": icon.strip()
            }
            hisse_list.append(hisse)
    
    # Veriyi sayfalara böl ve istenen sayfayı döndür
    start_index = (page - 1) * limit
    end_index = start_index + limit
    return hisse_list[start_index:end_index]

@app.route('/', methods=['GET'])
@cache.cached(timeout=3)  # Önbelleği 3sn için ayarla

def hisse_temel_endpoint():
    try:
        # İstekten page ve limit parametrelerini al
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        hisse_data = hisse_temel(page=page, limit=limit)
        return jsonify(hisse_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

    
@app.route('/test', methods=['GET'])
def test_enpoint():
    hisse_data = hisse_temel()[:5]  # İlk 5 hisseyi al
    return jsonify(hisse_data)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
