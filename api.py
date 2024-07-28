from bs4 import BeautifulSoup
import requests
from flask import Flask, json, request, jsonify
from flask_caching import Cache

app = Flask(__name__)

# Önbellekleme yapılandırması
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

URL = "https://borsa.doviz.com/hisseler"
hisse_list = []

def hisse_temel():
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
            hisse = {
                "Hisse Adi": hisse_adi[1],
                "Hisse_Kodu": hisse_adi[0],
                "Anlik fiyat": anlik.text.strip(),
                "Yuksek": yuksek.text.strip(),
                "Dusuk": dusuk.text.strip(),
                "Hacim": hacim.text.strip(),
                "Degisim": degisim.text.strip(),
                "Saat": saat.text.strip()
            }
            hisse_list.append(hisse)
    return hisse_list

@app.route('/hisse-temel', methods=['GET'])
@cache.cached(timeout=3)  # Önbelleği 3sn için ayarla
def hisse_temel_endpoint():
    hisse_data = hisse_temel()
    return jsonify(hisse_data)

@app.route('/', methods=['GET'])
@cache.cached(timeout=3)  # Önbelleği 3sn için ayarla
def home_page():
    data_set = hisse_temel()
    json_dump = json.dumps(data_set)
    return json_dump

'''
#yfinance verileri grafik için çekmek zahmetli ve verimsiz olabilir
@app.route('/hist/', methods=['GET'])
@cache.cached(timeout=3)
def history_page():
    data_set = {}
    
    for symbol in stockSymbols.stock_symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            data_set[symbol] = hist.to_dict()
        except Exception as e:
            data_set[symbol] = {'error': str(e)}
    
    json_dump = json.dumps(data_set)
    return json_dump
'''
if __name__ == '__main__':
    app.run(port=8080)
