from flask import Flask, render_template, request
from amazon_products import extract_data, get_price_change
import pandas as pd
import datetime

app = Flask(__name__)

@app.route('/')
def search():
    return render_template('search.html')

@app.route('/results', methods=['POST'])
def results():
    keyword = request.form.get('keyword')
    num_pages = request.form.get('num_pages')
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    filter_name = request.form.get('filter_name')

    current_date = datetime.datetime.now().strftime("%Y%m%d%H")

    if keyword and num_pages:
        try:
            num_pages = int(num_pages)
            extract_data(keyword, num_pages, current_date)
            products = get_price_change(current_date)
        except ValueError:
            return "Please enter a valid number of pages"
    else:
        try:
            products = pd.read_csv('price_change.csv')
            if min_price and max_price:
                min_price = int(min_price)
                max_price = int(max_price)
                products = products[(products['price'] >= min_price) & (products['price'] <= max_price)]
            if filter_name:
                products = products[products['name'].str.contains(filter_name, case=False)]
        except ValueError:
            return "Please enter a valid price range"
    return render_template('results.html', products=products.to_html(escape=False))


if __name__ == '__main__':
    app.run(debug=True)
