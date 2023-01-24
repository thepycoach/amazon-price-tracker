import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep


def extract_data(keyword, number_of_pages, current_date):
    driver = webdriver.Chrome('/Users/frankandrade/Downloads/chromedriver')
    keyword = '+'.join(keyword.split())

    elements = []
    prices = []
    images = []
    for page in range(1, number_of_pages+1):
        driver.get(f"https://www.amazon.com/s?k={keyword}&page={page}")
        sleep(2)
        rows = driver.find_elements(By.XPATH, '//div[contains(@class, "s-card-container")]')
        for row in rows:
            try:
                element = row.find_element(By.XPATH, './/span[@class="a-size-medium a-color-base a-text-normal"]').text
                price = row.find_element(By.XPATH, './/span[@class="a-price-whole"]').text
                image_link = row.find_element(By.XPATH, './/img[@class="s-image"]').get_attribute("src")
                image = f'<img src="{image_link}" width="60">'
                price = ''.join(price.split(','))
                elements.append(element)
                prices.append(price)
                images.append(image)
            except:
                pass

    df = pd.DataFrame({'name': elements, 'price': prices, 'image': images})
    df["date"] = current_date
    df.to_csv(f"{current_date}.csv", index=False)
    driver.close()
    return df


def get_price_change(current_date):
    df_lists = []
    for file in os.listdir():
        if file.endswith('.csv') and file not in ["price_change.csv"]:
            df = pd.read_csv(file)
            df.dropna(inplace=True)
            df.drop_duplicates(inplace=True)
            df = df.astype({'price': int})
            df_lists.append(df)

    df_concat = pd.concat(df_lists, ignore_index=True, axis=0)
    df_pivot = df_concat.pivot(index='date', columns='name', values='price')

    price_change = df_pivot.iloc[-1] - df_pivot.iloc[0]
    df_price_change = pd.DataFrame({"price change": price_change}).reset_index()

    df_last_update = pd.read_csv(f"{current_date}.csv")
    df_final = pd.merge(df_last_update, df_price_change, on="name")
    df_final = df_final.sort_values(by="price change")
    df_final = df_final[["name", "image", "price", "price change"]]
    df_final.to_csv("price_change.csv", index=False)
    return df_final