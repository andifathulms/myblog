import os
import shortuuid

from bs4 import BeautifulSoup

from django.utils import timezone
from django.template.defaultfilters import slugify


class FilenameGenerator(object):
    """
    Utility class to handle generation of file upload path
    """
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def __call__(self, instance: object, filename: str) -> str:
        today = timezone.localdate()

        filepath = os.path.basename(filename)
        filename, extension = os.path.splitext(filepath)
        filename = slugify(shortuuid.uuid()[:10])

        path = "/".join([
            self.prefix,
            today.strftime('%Y/%m/%d'),
            filename + extension
        ])
        return path


try:
    from django.utils.deconstruct import deconstructible
    FilenameGenerator = deconstructible(FilenameGenerator)  # type: ignore
except ImportError:
    pass


def get_table_of_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table_of_content = []

    for i, tag in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
        if not tag.get('id'):
            tag['id'] = f'heading-{i}'  # Auto-generate an ID if missing
        table_of_content.append({
            'level': int(tag.name[1]),
            'id': tag['id'],
            'text': tag.get_text(),
        })

    return table_of_content, str(soup)


def get_post_view_threshold(views: int) -> int:
    if views <= 5:
        return 1
    elif views <= 20:
        return 3
    elif views <= 50:
        return 5
    elif views <= 100:
        return 7
    else:
        return 10
