import csv
import xml.etree.ElementTree as ET
import html2text
from datetime import datetime


def remove_html_tags(content):
    if content is None:
        return ""
    html_converter = html2text.HTML2Text()
    html_converter.ignore_links = True
    html_converter.ignore_images = True
    plain_text = html_converter.handle(content)
    return plain_text.strip()


def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root


def filter_articles(root, start_year=2016):
    articles = []
    for item in root.findall('./channel/item'):
        post_date = item.find('{http://wordpress.org/export/1.2/}post_date').text
        post_date_dt = datetime.strptime(post_date, "%Y-%m-%d %H:%M:%S")

        if post_date_dt.year < start_year:
            continue

        title = item.find('title').text
        link = item.find('link').text
        content = remove_html_tags(item.find('{http://purl.org/rss/1.0/modules/content/}encoded').text)
        excerpt = remove_html_tags(item.find('{http://wordpress.org/export/1.2/excerpt/}encoded').text)
        author = item.find('{http://purl.org/dc/elements/1.1/}creator').text

        articles.append((title, link, content, excerpt, author, post_date))
    return articles


def write_csv(file_path, articles):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Link', 'Content', 'Excerpt', 'Author', 'Date'])
        for article in articles:
            writer.writerow(article)


def preprocess():
    root = parse_xml('data_raw/e-dialog.WordPress.2023-04-12.xml')
    articles = filter_articles(root)
    write_path = 'docs/articles.csv'
    write_csv(write_path, articles)
    print(f'wrote {len(articles)} articles to {write_path}')


if __name__ == "__main__":
    preprocess()
