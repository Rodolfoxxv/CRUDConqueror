import csv
from playwright.sync_api import sync_playwright

base_url = "https://www.mercadolivre.com.br"
csv_filepath = "C:\\Users\\rodol\\Downloads\\produtos_mais_vendidos.csv"  # Ajuste o caminho se necessário

# Função para extrair os dados do produto
def extract_product_data(product):
    # ID do Produto
    product_id = product.query_selector('a.ui-recommendations-card__link').get_attribute('href').split('/')[2].split('-')[0]

    # Título do Produto
    title = product.query_selector('p.ui-recommendations-card__title').inner_text().strip()

    # Preço Original
    try:
        price = product.query_selector('s.andes-money-amount.ui-recommendations-card__price-original-price').inner_text().strip()
        price = price.replace("R$", "").replace("\n", "").replace(",", ".").strip()  # Limpa o preço
    except AttributeError:
        price = None

    # Preço de venda
    try:
        sale_price = product.query_selector('span.andes-money-amount.ui-recommendations-card__price').inner_text().strip()
        sale_price = sale_price.replace("R$", "").replace("\n", "").replace(",", ".").strip()  # Limpa o preço
    except AttributeError:
        sale_price = None

    # Corrigindo o ID do produto
    if 'produto.mercadolivre.com.br' in product_id:
        product_id = product_id.split('/')[-1]

    return {
        'product_id': product_id,
        'title': title,
        'price': price,
        'sale_price': sale_price
    }

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # Acessa a página principal de categorias (Top Produtos de Construção)
    page.goto("https://www.mercadolivre.com.br/mais-vendidos/MLB1500")
    page.wait_for_selector('aside.ui-search-sidebar')

    # Extrai o nome da categoria principal
    main_category_name = page.query_selector('h2.ui-search-breadcrumb__title').inner_text().strip().replace("Mais vendidos em  ", "")

    # Extrai as informações das categorias (nome e URL)
    categories = [(main_category_name, page.url)]  # Adiciona a categoria principal
    category_links = page.query_selector_all('aside.ui-search-sidebar li.ui-search-filter-container a.ui-search-link')
    for category_link in category_links:
        category_url = category_link.get_attribute('href')
        category_name = category_link.query_selector('span.ui-search-filter-name').inner_text().strip()
        categories.append((category_name, category_url))

    all_product_data = []

    # Extrai os produtos da página principal
    products = page.query_selector_all('div.ui-recommendations-card--vertical')
    for product in products:
        product_data = extract_product_data(product)
        product_data['category'] = main_category_name
        all_product_data.append(product_data)

    # Itera pelas categorias (exceto a principal)
    for category_name, category_url in categories[1:]:  # Começa da segunda categoria
        print(f"Extraindo produtos da categoria: {category_name}")

        # Acessa a página da categoria
        page.goto(category_url)
        page.wait_for_selector('div.ui-recommendations-card')

        products = page.query_selector_all('div.ui-recommendations-card--vertical')
        for product in products:
            product_data = extract_product_data(product)
            product_data['category'] = category_name
            all_product_data.append(product_data)

    browser.close()

    # Salva os dados em um arquivo CSV
    with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product_id', 'title', 'price', 'sale_price', 'category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for product in all_product_data:
            writer.writerow(product)