import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# Definir o caminho para salvar o arquivo
output_path = r"C:\Users\SE60731\Downloads"

base_url = 'https://www.cristianocec.com.br/loja/catalogo.php?loja=1028926&categoria=515'
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

product_names = []
original_prices = []
discounted_prices = []
product_ids = []

page_number = 1
product_id = 1

while product_id <= 3000:  # Limitar a 3000 produtos
    url = f"{base_url}&pg={page_number}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        products = soup.find_all('div', class_='product show-down')

        # Se não encontrarmos produtos na página, assumimos que chegamos ao fim
        if not products:
            break

        for product in products:
            product_name = product.find('div', class_='product-name').text.strip()
            price_before = product.find('div', id=lambda x: x and x.startswith('pricebefore-'))
            original_price = price_before.text.strip() if price_before else None
            price_off = product.find('div', id=lambda x: x and x.startswith('priceoff-'))
            discounted_price = price_off.text.strip() if price_off else None

            product_names.append(product_name)
            original_prices.append(original_price)
            discounted_prices.append(discounted_price)
            product_ids.append(product_id)

            product_id += 1
            if product_id > 1000:  # Sair do loop se atingir o limite
                break

        page_number += 1
        time.sleep(1)  # Aguardar 1 segundo entre as requisições (ajuste conforme necessário)

    else:
        print(f"Erro na requisição: {response.status_code}")
        break

# Criar um dicionário com os dados
data = {
    'ID': product_ids,
    'NomedoProduto': product_names,
    'PrecoOriginal': original_prices,
    'PrecoDesconto': discounted_prices,
}

# Converter o dicionário em um DataFrame Pandas
df = pd.DataFrame(data)

# Salvar o DataFrame como CSV
file_path = os.path.join(output_path, "produtos.csv")
df.to_csv(file_path, sep=';', encoding='utf-8-sig', index=False)

print(f"DataFrame salvo como '{file_path}'")