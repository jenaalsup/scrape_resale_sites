import argparse
import requests
from lxml import html
from price_parser import Price

stats = ""
sold_stats = ""
scraped_products = []
available_value = 0
sold_value = 0
final_global_value = 0

def ebay_parse_available(brand):
  global stats
  global available_value

  page_num = 1
  scraped_products = []
  total_value = 0
  total_count = 0

  while True:
    url = 'https://www.ebay.com/sch/i.html?_nkw="{0}"&_sacat=0&_dmd=1&_sop=10&_ipg=200&_pgn={1}'.format(brand, page_num) # sorts by newly listed
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    failed = False

    # Retries for handling network errors
    for _ in range(5):
      print ("Retrieving %s\n\n"%(url)) 
      response = requests.get(url, headers=headers, verify=True)
      parser = html.fromstring(response.text)
      print("Done retrieving")

      if response.status_code!=200: 
        print("eBay URL request failed to respond, retrying...")
        failed = True
        continue
      else:
        print("Available page num :", page_num)
        failed = False
        break

      if failed:
        print("The eBay network is unresponsive. Please try again later (or now).")
        return []

    product_listings = parser.xpath('//li[contains(@class, "s-item    ")]')
    raw_result_count = parser.xpath("//h1[contains(@class,'count-heading')]//text()")

    if raw_result_count == None: 
      print("NILNILNIL")
    if len(raw_result_count) < 1:
      print("0000000000")
      continue
    result_count = raw_result_count[0]
    result_count = result_count.replace(',', "")

    count = 0
    for product in product_listings:
      raw_url = product.xpath('.//a[contains(@class,"item__link")]/@href')
      raw_title = product.xpath('.//h3[contains(@class,"item__title")]//text()')
      raw_product_type = product.xpath('.//h3[contains(@class,"item__title")]/span[@class="LIGHT_HIGHLIGHT"]/text()')
      raw_price = product.xpath('.//span[contains(@class,"s-item__price")]//text()')
      raw_title[0].encode('ascii', 'ignore')
      sponsored = product.xpath('.//span[contains(@role,"text")]//text()')
      if (len(sponsored) > 0): # don't count sponsored products
          continue

      count = count + 1
      price  = ' '.join(' '.join(raw_price).split())
      parsed_price = Price.fromstring(price)
      total_value = total_value + parsed_price.amount_float
      title = ' '.join(' '.join(raw_title).split())
      product_type = ''.join(raw_product_type)
      title = title.replace(product_type, '').strip()

      data = {
                  'url':raw_url[0],
                  'title':title,
                  'price':price, 
                  'sold':"Available"
      }
      scraped_products.append(data)
    if scraped_products:
      total_count = total_count + count
      if count < 200:
        value = (total_value / total_count) * int(result_count)
        stats = "  AVAILABLE STATS for Brand: %s   Items Scanned: %d   Total Items (Including sponsored): %d   Value (Without sponsored): $%0.2f "%( brand, 
        total_count, int(result_count), value) 
        available_value = value  
        print(stats)
        print("-------> DONE WITH AVAILABLE!")
        break
      page_num = page_num + 1
    else:
      print("No available product listings on eBay")
      break
  return scraped_products

def ebay_parse_sold(brand):
  global sold_stats
  global sold_value

  page_num = 1
  scraped_products = []
  total_value = 0
  total_count = 0

  while True:
    url = 'https://www.ebay.com/sch/i.html?_nkw="{0}"&_sacat=0&_dmd=1&_sop=10&LH_Complete=1&_ipg=200&_pgn={1}'.format(brand, page_num) # sorts by newly listed
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    failed = False

    # Retries for handling network errors
    for _ in range(5):
      print ("Retrieving %s\n\n"%(url)) 
      response = requests.get(url, headers=headers, verify=True)
      parser = html.fromstring(response.text)
      print("Done retrieving")

      if response.status_code!=200:
        print("eBay URL request failed to respond, retrying...")
        failed = True
        continue
      else:
        print("Sold page num :", page_num)
        failed = False
        break

    if failed:
      print("The eBay network is unresponsive. Please try again later (or now).")
      return []

    product_listings = parser.xpath('//li[contains(@class, "s-item    ")]')
    print("PRODUCT LISTINGS:", product_listings)
    raw_result_count = parser.xpath("//h1[contains(@class,'count-heading')]//text()")

    if raw_result_count == None: 
        print("NILNILNIL")
    if len(raw_result_count) < 1:
        print("0000000000")
        continue
    result_count = raw_result_count[0]
    result_count = result_count.replace(',', "")

    count = 0
    for product in product_listings:
      raw_url = product.xpath('.//a[contains(@class,"item__link")]/@href')
      raw_title = product.xpath('.//h3[contains(@class,"item__title")]//text()')
      raw_title[0].encode('ascii', 'ignore')
      raw_product_type = product.xpath('.//h3[contains(@class,"item__title")]/span[@class="LIGHT_HIGHLIGHT"]/text()')
      raw_price = product.xpath('.//span[contains(@class,"s-item__price")]//text()')
      raw_sold_date = product.xpath('.//span[contains(@class,"s-item__ended-date")]//text()')
      print("RAW SOLD DATE: ", raw_sold_date)

      count = count + 1
      price  = ' '.join(' '.join(raw_price).split())
      parsed_price = Price.fromstring(price)
      total_value = total_value + parsed_price.amount_float
      title = ' '.join(' '.join(raw_title).split())
      product_type = ''.join(raw_product_type)
      title = title.replace(product_type, '').strip()
      sold_date = raw_sold_date[0].split()[0]
      print("SOLD DATE: ", sold_date)

      data = {
                  'url':raw_url[0],
                  'title':title,
                  'price':price, 
                  'sold':"Sold: "+sold_date
      }
      scraped_products.append(data)

    if scraped_products:
      total_count = total_count + count
      if count < 200:
        value = (total_value / total_count) * int(result_count)
        sold_stats = "  SOLD STATS for Brand: %s   Total Sold Items: %d   Value: $%0.2f "%( brand, 
        total_count, value)   
        print(sold_stats)
        sold_value = value
        print("-------> DONE WITH SOLD!")
        break
      page_num = page_num + 1
    else:
      print("No sold product listings on eBay")
      break
  return scraped_products

def poshmark_parse_available(brand):
  global stats 
  global available_value 

  page_num = 1 
  # scraped_products = []
  total_value = 0 
  total_count = 0 

  # change spaces in the brand name to '%20' to match the poshmark url
  url_brand = (brand.replace(' ', '%20')).lower()

  while True:
    url = 'https://poshmark.com/search?query={0}&sort_by=added_desc&max_id={1}'.format(url_brand, page_num) # sorts by just in
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    failed = False

    # Retries 5 times for handling network errors
    for _ in range(5):
      print ("Retrieving %s\n\n"%(url)) 
      response = requests.get(url, headers=headers, verify=True)
      parser = html.fromstring(response.text)
      print("Done retrieving")

      if response.status_code!=200:
          failed = True
          continue
      else:
          print("Available page num :", page_num)
          failed = False
          break

    if failed:
      print("The Poshmark network is unresponsive. Please try again later (or now).")
      return []

    product_listings = parser.xpath('//div[contains(@class, "card card--small")]')  
    count = 0
    for product in product_listings:
      raw_url = product.xpath('.//a[contains(@class,"tile__covershot")]/@href')
      raw_title = product.xpath('.//a[contains(@class,"tile__title")]//text()')
      raw_price = product.xpath('.//span[contains(@class,"p--t--1")]//text()')
      raw_title[0].encode('ascii', 'ignore')

      count = count + 1
      product_url = 'https://poshmark.com' + raw_url[0]
      title = ' '.join(' '.join(raw_title).split())
      price  = ' '.join(' '.join(raw_price).split())
      parsed_price = Price.fromstring(price)
      total_value = total_value + parsed_price.amount_float

      data = {
                  'url':product_url,
                  'title':title,
                  'price':price, 
                  'sold':"Available"
      }
      scraped_products.append(data)

    if scraped_products:
      total_count = total_count + count
      if count < 48: # 48 items per page on Poshmark
        stats = "  AVAILABLE STATS for Brand: %s   Items Scanned: %d   Total Value: $%0.2f "%( brand, 
        total_count, total_value)
        available_value = total_value  
        print(stats)
        print("-------> DONE WITH AVAILABLE!")
        break
      page_num = page_num + 1
    else:
      print("No available product listings on Poshmark")
      break
  return scraped_products

def poshmark_parse_sold(brand):
  global sold_stats 
  global sold_value 

  page_num = 1 
  total_value = 0 
  total_count = 0 

  # change spaces in the brand name to '%20' to match the poshmark url
  url_brand = (brand.replace(' ', '%20')).lower()

  while True:
    url = 'https://poshmark.com/search?query={0}&availability=sold_out&sort_by=added_desc&max_id={1}'.format(url_brand, page_num) # sorts by just in
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    failed = False

    # Retries 5 times for handling network errors
    for _ in range(5):
      print ("Retrieving %s\n\n"%(url)) 
      response = requests.get(url, headers=headers, verify=True)
      parser = html.fromstring(response.text)
      print("Done retrieving")

      if response.status_code!=200:
        failed = True
        continue
      else:
        print("Sold page num :", page_num)
        failed = False
        break

    if failed:
      print("The Poshmark network is unresponsive. Please try again later (or now).")
      return []

    product_listings = parser.xpath('//div[contains(@class, "card card--small")]')

    count = 0
    for product in product_listings:
      raw_url = product.xpath('.//a[contains(@class,"tile__covershot")]/@href')
      raw_title = product.xpath('.//a[contains(@class,"tile__title")]//text()')
      raw_price = product.xpath('.//span[contains(@class,"p--t--1")]//text()')
      raw_title[0].encode('ascii', 'ignore')

      count = count + 1
      product_url = 'https://poshmark.com' + raw_url[0]
      title = ' '.join(' '.join(raw_title).split())
      price  = ' '.join(' '.join(raw_price).split())
      parsed_price = Price.fromstring(price)
      total_value = total_value + parsed_price.amount_float

      data = {
                  'url':product_url,
                  'title':title,
                  'price':price, 
                  'sold':"Sold"
      }
      scraped_products.append(data)

    if scraped_products:
      total_count = total_count + count
      if count < 48: # 48 items per page on Poshmark
        sold_stats = "  SOLD STATS for Brand: %s   Items Scanned: %d   Total Value: $%0.2f "%( brand, 
        total_count, total_value)
        sold_value = total_value  
        print(sold_stats)
        print("-------> DONE WITH SOLD!")
        break
      page_num = page_num + 1
    else:
      print("No sold product listings on Poshmark")
      break
  return scraped_products

def thredup_parse_available(brand):
  global stats 
  global available_value 

  page_num = 1 
  total_value = 0 
  total_count = 0 

  # change spaces in the brand name to '%20' to match the thredup url
  url_brand = (brand.replace(' ', '%20')).lower()

  while True:
    url = 'https://www.thredup.com/women?department_tags=women&sort=newest_first&text={0}&page={1}'.format(url_brand, page_num) # sorts by newly listed
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    failed = False

    # Retries 5 times for handling network errors
    for _ in range(5):
      print ("Retrieving %s\n\n"%(url)) 
      response = requests.get(url, headers=headers, verify=True)
      parser = html.fromstring(response.text)
      print("Done retrieving")

      if response.status_code!=200:
        failed = True
        continue
      else:
        print("Available page num :", page_num)
        failed = False
        break

    if failed:
        print("The thredUP network is unresponsive. Please try again later (or now).")
        return []

    product_listings = parser.xpath('//div[contains(@class, "grid-item")]')
 
    count = 0
    for product in product_listings:
      raw_url = product.xpath('.//a[contains(@class,"_1di0il_2VkBBwWJz9eDxoJ")]/@href')
      raw_title_and_price = product.xpath('.//div[contains(@class,"_138U7gqcrSxaloaCpyMPZg")]//text()')
      raw_title_and_price[0].encode('ascii', 'ignore')

      count = count + 1
      product_url = 'https://thredup.com' + raw_url[0]
      title = raw_title_and_price[0]
      price  = '$' + raw_title_and_price[2] 
      parsed_price = Price.fromstring(price)
      total_value = total_value + parsed_price.amount_float

      data = {
                  'url':product_url,
                  'title':title,
                  'price':price, 
                  'sold':"Available"
      }
      scraped_products.append(data)

    if scraped_products:
        total_count = total_count + count
        if count < 50: # 50 items per page on thredUP
            stats = "  AVAILABLE STATS for Brand: %s   Items Scanned: %d   Value (Without sponsored): $%0.2f "%( brand, 
            total_count, total_value)
            available_value = total_value  
            print(stats)
            print("-------> DONE WITH AVAILABLE!")
            break
        page_num = page_num + 1
    else:
        print("No available product listings on thredUP")
        break
  return scraped_products

def save_scraped_data(website, sdata, brand):
  global final_global_value
  if sdata:
    if website == 'ebay':
      file_name = "eBay_" + str(brand) + ".csv"
    elif website == 'poshmark':
      file_name = "Poshmark_" + str(brand) + ".csv"
    elif website == 'thredup':
      file_name = "thredUP_" + str(brand) + ".csv"
    else:
      file_name = str(brand) + ".csv"

    f = open(file_name,"w+")
    f.write("\"title\", price, sold, url\r\n")

    total_value_stats = "  TOTAL VALUE OF AVAILABLE AND SOLD ITEMS: $" + str(available_value + sold_value)
    final_global_value = final_global_value + available_value + sold_value
    print(total_value_stats)
    f.write( stats) 
    f.write("\r\n")
    f.write(sold_stats)
    f.write( "\r\n" )
    f.write(total_value_stats)
    f.write( "\r\n" )

    for data in sdata:
      f.write("\"" + data['title'] + "\", ")
      new_price = data['price'].replace(',', "")
      f.write( new_price + ", ")
      f.write( data['sold'] + ", ")
      f.write( data['url'] + "\r\n")
    f.close() 
  else:
    print("No data scraped")
  return

# main code entry point
if __name__=="__main__":
  argparser = argparse.ArgumentParser()
  argparser.add_argument('brand',help = 'Brand Name')
  args = argparser.parse_args()
  brand = args.brand

  # ebay
  ebay_scraped_data = ebay_parse_available(brand)
  ebay_scraped_data = ebay_scraped_data + ebay_parse_sold(brand)
  save_scraped_data('ebay', ebay_scraped_data, brand)
  print("DONE WITH EBAY")

  # poshmark
  poshmark_scraped_data = poshmark_parse_available(brand)
  poshmark_scraped_data = poshmark_scraped_data + poshmark_parse_sold(brand)
  save_scraped_data('poshmark', poshmark_scraped_data, brand)
  print("DONE WITH POSHMARK")

  # thredup
  scraped_data = thredup_parse_available(brand)
  save_scraped_data('thredup', scraped_data, brand)
  print("DONE WITH THREDUP")

  print("TOTAL VALUE OF ALL ITEMS ON EBAY, POSHMARK, THREDUP: " + str(final_global_value))
