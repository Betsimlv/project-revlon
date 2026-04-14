import pandas as pd
import json
import re
import time
import os
import sys
import logging
from psycopg2 import sql, Error
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains




sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from utils.utils import *


elements = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "map",
    "elements-html.json",
)

with open(elements, "r", encoding="utf-8") as f:
    elements_html = json.load(f)

queries = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "map", "query.json"
)

with open(queries, "r", encoding="utf-8") as f:
    query = json.load(f)


def popup_window(driver):

    try:
        form_submit = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, elements_html["popup_window"])
            )
        )
    except TimeoutException:
        form_submit = False

    if form_submit:
        return driver.find_element(
            By.CSS_SELECTOR, elements_html["popup_window_close"]
        ).click()


def products_info_for_collection():

    collections = [
        "https://www.revlon.com/collections/face",
        "https://www.revlon.com/collections/lips",
        "https://www.revlon.com/collections/eyes",
        "https://www.revlon.com/collections/nails",
        "https://www.revlon.com/collections/hair",
        "https://www.revlon.com/collections/super-lustrous-collection",
        "https://www.revlon.com/collections/colorstay-collection",
        "https://www.revlon.com/collections/new",
    ]

    driver = webdriver.Chrome()
    all_data = []

    for collection in collections:
        driver.get(collection)

        popup_window(driver)

        all_products = driver.find_elements(
            By.CLASS_NAME, elements_html["info_products"]["href"]
        )

        for i in range(len(all_products)):
            try:
                collections_name_db = re.search(r"[^/]+$", collection).group()
                product_link_db = all_products[i].get_attribute("href")
                product_name_db = (
                    all_products[i]
                    .find_element(
                        By.CLASS_NAME, elements_html["info_products"]["title"]
                    )
                    .text
                )
                product_link_img_db = (
                    all_products[i]
                    .find_element(
                        By.CSS_SELECTOR, elements_html["info_products"]["image"]
                    )
                    .get_attribute("src")
                )

                price_db = (
                    all_products[i]
                    .find_element(
                        By.CLASS_NAME, elements_html["info_products"]["price"]
                    )
                    .text
                )

            except Exception as e:
                print(f"Error en el producto {i} de la colección {collection}: {e}")
                continue

            datos = (
                collections_name_db,
                product_name_db,
                product_link_db,
                product_link_img_db,
                price_db,
            )

            all_data.append(datos)

    df = pd.DataFrame(
        all_data,
        columns=[
            "collection_name",
            "product_name",
            "product_link",
            "product_image",
            "price",
        ],
    )

    df_unique = df.drop_duplicates(subset=["product_link"], keep="first")

    return df_unique


def details_products(products_info_for_collection, conn_params):

    all_data_details = []
    driver = webdriver.Chrome()

    for idex, row in products_info_for_collection.iterrows():
        product_link = row["product_link"]
        price = row["price"]
        image_product_link = row["product_image"]
        product_name = row["product_name"]
        collection_name = row["collection_name"]

        driver.get(row["product_link"])
        popup_window(driver)


        try:
            text_description = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, elements_html["details_products"]["description"][0])
                )
            )
            description = text_description.text

        except Exception:
            try:
                text_description = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            elements_html["details_products"]["description"][1],
                        )
                    )
                )
                description = text_description.text

            except Exception:
                description = "No se encontró la descripción"
                print(f"No se encontró la descripción del producto {link}")

        try:
            rating_counts = driver.find_elements(
                By.CSS_SELECTOR, elements_html["details_products"]["rating_counts"]
            )[0].text

            all_rating_counts = rating_counts.strip().split("\n")
        except Exception as e:
            try:
                rating_counts = driver.find_elements(
                    By.CSS_SELECTOR, elements_html["details_products"]["rating_counts"]
                ).text
                print("no era lista")
            except Exception as e:
                all_rating_counts = ""
                print(e)

        tabla = "collections_new"
        columna = "collections_name"
        columna_es_igual = collection_name
        collection_id = get_ids(conn_params, tabla, columna, columna_es_igual)

        datos_details = (
            product_name,
            product_link,
            image_product_link,
            price,
            description,
            all_rating_counts,
            collection_id[0],
        )

        all_data_details.append(datos_details)

    df_details = pd.DataFrame(
        all_data_details,
        columns=[
            "product_name",
            "product_link",
            "product_link_img",
            "price",
            "description",
            "all_rating_counts",
            "collection_id",
        ],
    )
    df_details = df_details.drop_duplicates(subset=["product_link"], keep="first")

    df_details["counts_reviews"] = df_details["all_rating_counts"].apply(
        lambda x: sum(int(x[i]) for i in range(1, len(x), 2))
    )
    star = 0

    for j in range(5):
        star = star + 1

        df_details[f"star_{star}"] = df_details["all_rating_counts"].apply(
            lambda x: [x[i] for i in range(1, len(x), 2)][j] if x != "" else None
        )

    df_details = df_details[
        [
            "product_name",
            "product_link",
            "product_link_img",
            "price",
            "description",
            "counts_reviews",
            "star_5",
            "star_4",
            "star_3",
            "star_2",
            "star_1",
            "collection_id",
        ]
    ]

    data_insert_details = [tuple(row) for row in df_details.values]
    insert_query_details = query["tables"]["products_new"]

    data_insert(data_insert_details, insert_query_details, conn_params)

    return


def store_prices(products_info_for_collection, conn_params):
    
    all_data_prices = []
    driver = webdriver.Chrome()

    for idex, row in products_info_for_collection.iterrows():
        product_link = row["product_link"]

        driver.get(row["product_link"])
        popup_window(driver)
        
        iframe = driver.find_element(
            By.CSS_SELECTOR, elements_html["details_products"]["iframe"]
        )
        driver.switch_to.frame(iframe)

        see_more = driver.find_element(By.CSS_SELECTOR, "a[aria-label='See more']")
        driver.execute_script("arguments[0].click();", see_more)

        listitem = driver.find_element(
            By.ID, elements_html["details_products"]["stores_section"]
        )

        all_listitem = listitem.find_elements(
            By.CSS_SELECTOR, elements_html["details_products"]["items_stores"]
        )
        store_name = []
        store_price = []

        try:
            for i in range(len(all_listitem) - 1):
                store_name.append(
                    all_listitem[i]
                    .find_element(By.TAG_NAME, "img")
                    .get_attribute("alt")
                )

                store_price.append(
                    all_listitem[i].find_element(By.CLASS_NAME, "price").text
                )

        except Exception as e:
            print(f"Error al obtener el elemento de las Tiendas {e}")

        store_name = store_name
        store_price = store_price
        driver.switch_to.default_content()
        
        tabla = "products_new"
        columna_es_igual = product_link
        columna = "product_link"
        product_id = get_ids(conn_params, tabla, columna, columna_es_igual)

        datos_prices = (product_id[0], store_name, store_price)
        all_data_prices.append(datos_prices)
        
    df_prices = pd.DataFrame(
        all_data_prices, columns=["product_id", "store_name", "store_price"]
    )

    df_prices = df_prices.drop_duplicates(subset=["product_id"], keep="first")
    df_prices = df_prices.explode(["store_name", "store_price"])
    
    data_insert_prices = [tuple(row) for row in df_prices.values]

    insert_query_prices = query["tables"]["product_store_prices_new"]

    data_insert(data_insert_prices, insert_query_prices, conn_params)
    
    return



def comments_products(df_products_info_for_collection, conn_params):

    links = df_products_info_for_collection["product_link"]

    driver = webdriver.Chrome()

    for link in links:
        driver.get(link)

        popup_window(driver)

        all_data = []
        try:
            btn_next = WebDriverWait(driver, 1).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, elements_html["comments"]["next_page"])
                )
            )
            if not btn_next[0].is_enabled():
                print("El botón está deshabilitado. ¡Llegamos al final!")
                btn_next = False

        except TimeoutException:
            btn_next = False

        while btn_next:
            driver_0 = driver.find_elements(
                By.CSS_SELECTOR, 'section[class="shopify-section"]'
            )[0]

            time.sleep(0.5)

            reviews_comments = WebDriverWait(driver_0, 1).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, elements_html["comments"]["message"])
                )
            )
            reviews_comments_messages = driver_0.find_elements(
                By.CSS_SELECTOR, elements_html["comments"]["headers"][0]
            )
            reviews_comments_ratings = driver_0.find_elements(
                By.CSS_SELECTOR, elements_html["comments"]["headers"][2]
            )
            reviews_comments_date = driver_0.find_elements(
                By.CSS_SELECTOR, elements_html["comments"]["headers"][3]
            )
            reviews_comments_author = driver_0.find_elements(
                By.CSS_SELECTOR, elements_html["comments"]["author"]
            )

            for comments in range(len(reviews_comments)):
                try:
                    product_link = link

                    message_comments = safe_extract(reviews_comments, comments)
                    title_comments = safe_extract(reviews_comments_messages, comments)
                    dateCreated = safe_extract(reviews_comments_date, comments)
                    rating_comments = safe_extract(
                        reviews_comments_ratings, comments, "title"
                    )
                    author_comments = safe_extract(reviews_comments_author, comments)

                    try:
                        page = driver.find_element(
                            By.CSS_SELECTOR, elements_html["comments"]["page"]
                        ).get_attribute("page")

                    except (IndexError, AttributeError) as e:
                        page = ""
                        logger.warning(f"Error extracting page: {e}")

                    tabla = "products_new"
                    columna = "product_link"
                    columna_es_igual = product_link
                    product_id = get_ids(conn_params, tabla, columna, columna_es_igual)

                    data_comments = (
                        product_id[0],
                        title_comments,
                        author_comments,
                        rating_comments,
                        message_comments,
                        dateCreated,
                        page,
                    )

                    all_data.append(data_comments)

                except Exception as e:
                    print(f"Error al extraer comentarios - {link}")

            try:
                btn_next = WebDriverWait(driver_0, 1).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, elements_html["comments"]["next_page"])
                    )
                )

                if "disabled" in btn_next.get_attribute("class"):
                    print("El botón está deshabilitado. ¡Llegamos al final!")
                    btn_next = False
                else:
                    actions = ActionChains(driver)
                    actions.move_to_element(btn_next).perform()

                    time.sleep(1)

                    driver.execute_script("arguments[0].click();", btn_next)

            except TimeoutException:
                btn_next = False

        df = pd.DataFrame(
            all_data,
            columns=[
                "product_id",
                "title_comments",
                "author_comments",
                "rating_comments",
                "message_comments",
                "dateCreated",
                "page",
            ],
        )

        print(df.shape, link)
        df = df.drop_duplicates(
            subset=["title_comments", "author_comments", "message_comments"],
            keep="first",
        )

        df["rating_comments"] = df.rating_comments.apply(
            lambda x: int(x[0]) if x else 0
        )

        df["dateCreated"] = (
            pd.to_datetime(df["dateCreated"], format="%m/%d/%y", errors="coerce")
            .bfill()
            .ffill()
            .dt.date
        )

        df_insert = [tuple(row) for row in df.values]

        insert_query = query["tables"]["product_comments_new"]

        data_insert(df_insert, insert_query, conn_params)

    return df
