
def get_prerequisites():
    beg_url = input("Please enter a beginning url: ")
    end_url = input("Please enter an ending url: ")
    num_degrees = int(input("Enter the number of degrees: "))    
    return (beg_url, end_url, num_degrees)


def create_sql_database(beg_url):
    import sqlite3
    from time import time
    sql_filename = str(beg_url.split("/")[-1]) + str(time()) + ".sqlite"
    conn = sqlite3.connect(sql_filename)
    cur = conn.cursor()    
    cur.execute("""
                   CREATE TABLE Links (current_url TEXT, predecessor_url TEXT)
                   """)
    return conn, cur, sql_filename


def close_sql_database(conn,cur):
    conn.commit()
    cur.close()

    
def find_urls_on_page(beg_url):
    import urllib.request, urllib.parse, urllib.error
    import ssl
    from bs4 import BeautifulSoup
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    links_on_url = list()
    fhand = urllib.request.urlopen(beg_url, context=ctx)
    soup = BeautifulSoup(fhand, 'html.parser')   
    for tag in soup.find_all("a"):
                link = str(tag.get("href"))
                if link.startswith("/wiki/") and link.count(":") == 0:
                    rellink = "https://en.wikipedia.org"+link
                    links_on_url.append(rellink)
    return links_on_url


def recursive_search_function(url, beg_url, search_path_list, sql_filename):
    import sqlite3
    conn = sqlite3.connect(sql_filename)
    cur = conn.cursor()
    if url == beg_url:
        return search_path_list
    else:
        cur.execute('SELECT predecessor_url FROM Links WHERE current_url = ? ', (url,))
        predecessor_url = cur.fetchone()[0]
        search_path_list.append(predecessor_url)
        return recursive_search_function(predecessor_url, beg_url, search_path_list, sql_filename)
   


def six_degrees():
    degree_counter = 0   
    all_urls_list = list()
    beg_url, end_url, num_degrees = get_prerequisites()    
    create_sql_database(beg_url)
    conn, cur, sql_filename = create_sql_database(beg_url)
    find_urls = [beg_url]
    found_url = False
    search_path_list = list()
    
    if degree_counter == 0:
        cur.execute("INSERT INTO Links (current_url, predecessor_url) VALUES (?, ?)", (beg_url,beg_url))
    if end_url == beg_url:
        return f'FOUND URL AT {beg_url}. Number of degrees: {degree_counter}'
    if end_url != beg_url:
        for degree in range(num_degrees):
            if found_url == True:
                break
            degree_counter += 1
            for url in find_urls:
                if url in all_urls_list:
                    continue
                links_on_url = find_urls_on_page(url)
                if end_url in links_on_url:
                    cur.execute("INSERT INTO Links (current_url, predecessor_url) VALUES (?, ?)", (end_url,url))                    
                    found_url = True
                    break
                for link in links_on_url:
                    cur.execute('SELECT current_url FROM Links WHERE current_url = ? ', (link,))
                    row = cur.fetchone()
                    if row is None:
                        cur.execute("INSERT INTO Links (current_url, predecessor_url) VALUES (?, ?)", (link,url))                    
                    all_urls_list.append(link)
                    if link == end_url:
                        break
            if end_url not in all_urls_list:
                find_urls = []
                for url in all_urls_list: 
                    if url not in find_urls:
                        find_urls.append(url)
                all_urls_list = []    
    if found_url == True:
        close_sql_database(conn, cur) 
        search_path_list.append(end_url)
        recursive_search_function(end_url, beg_url, search_path_list, sql_filename)
        return f"FOUND END URL: {end_url}! NUMBER OF DEGREES: {degree_counter}. SEARCH PATH: {search_path_list[::-1]}"
    if found_url == False:       
        return f"SORRY, DID NOT FIND END URL {end_url} in {degree_counter} DEGREES."   
    close_sql_database(conn, cur) 


    
