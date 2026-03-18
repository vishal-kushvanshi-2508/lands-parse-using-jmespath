from lxml import html
import os
from parsel import Selector
import json
import gzip

## get html content using url

# def read_html_content(url):
#     headers = {
#         "User-Agent": "Mozilla/5.0"
#     }
#     response = requests.get(url, headers=headers)
#     tree = html.fromstring(response.text)

#     # convert to formatted HTML
#     formatted_html = etree.tostring(tree, pretty_print=True, encoding="unicode")
#     with open("wendys_html_content.html", "w", encoding="utf-8") as f:
#         f.write(formatted_html)
#     return formatted_html


## get html content using direct file

def read_html_content(file_name):
    current_working_dir = os.getcwd()
    file_path = f"{current_working_dir}/{file_name}"
    with gzip.open(file_path, "rt", encoding='utf-8') as f :
        html_content = f.read()
    
    ## this is use for store html content in file  
    # with open("product_data.html", "w", encoding="utf-8") as f:
    #     f.write(html_content)
    
    return html_content

## this function is use for parse nested json data and convert to useful json data  
def parse_nested_json(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
        
            if isinstance(value, str):
                value_strip = value.strip()
                if (value_strip.startswith("{") and value_strip.endswith("}")) or (value_strip.startswith("[") and value_strip.endswith("]")):

                    value = json.loads(value_strip)

            new_obj[key] = parse_nested_json(value)
        return new_obj
    
    else:
        return obj


def extract_data_from_html(html_content):
    product_list = []
    tree = html.fromstring(html_content)
    raw = tree.xpath('string(//script[@id="app-root-state"])')
    ## first cleaning json data
    clean = (raw.replace('&q;', '"').replace('&s;', "'").replace('&a;', '&').replace('&g;', '>').replace('&l;', '<'))
    # 🔥 Convert string to JSON
    data = json.loads(clean)

    # store in file
    # with open("clean_data.json", "w", encoding="utf-8") as f:
    #     json.dump(data, f, indent=4, ensure_ascii=False)
    
    ## second cleaning of json data and convert usefull short json data
    json_data = parse_nested_json(data)

    ## store in file  
    # with open('land.json', 'w', encoding='utf-8') as f:
    #     json.dump(json_data, f, indent=4)
    
    ## crate selector object and extract data using jmespath
    selector = Selector(text=json.dumps(json_data["/le-api/pub/product-lookup/product?productId=401068"] ) , type="json")
    
    product_id = selector.jmespath('productDetail.number').get()

    product_name = selector.jmespath('productDetail.productCopies[0].description').get()
    
    product_url = selector.jmespath('pageMetaOverride.openGraphTags[2].content').get()
    
    brand_name = selector.jmespath('productDetail.brandName').get()
    product_dict = {
        "product_id" : product_id,
        "product_name" : product_name,
        "product_url" : product_url,
        "brand_name" : brand_name
    }
    
    ## extract variant data
    skus_list = selector.jmespath("productDetail.skus")
    variante_list = []
    for data in skus_list:
        dict_data = {}

        dict_data["styleNumber"] = data.jmespath("styleNumber").get()
        dict_data["size_code"] = data.jmespath("sizeCode").get()

        dict_data["currentPrice"] = data.jmespath("price.currentPrice").get()
        dict_data["originalPrice"] = data.jmespath("price.originalPrice").get()

        dict_data["size_longLabel"] = data.jmespath("size.values[0].longLabel").get()
        dict_data["size_label"] = data.jmespath("size.values[0].label").get()

        dict_data["size_range"] = data.jmespath("attributeTypes[0].values[0].label").get()
        dict_data["fit"] = data.jmespath("attributeTypes[1].values[0].label").get()

        dict_data["colour_label"] = data.jmespath("color.values[0].swatches[0].label").get()
        dict_data["colorFamily"] = data.jmespath("color.values[0].swatches[0].colorFamily").get()
        dict_data["imageUrl"] = data.jmespath("color.values[0].swatches[0].imageUrl").get()
        
        variante_list.append(dict_data)
    product_dict["variants"] = json.dumps(variante_list)
    product_list.append(product_dict)
    
    return product_list


