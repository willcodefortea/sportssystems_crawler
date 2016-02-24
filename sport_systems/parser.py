from bs4 import BeautifulSoup


def parse(xml):
    """Parse an XML response from the SportsSystem API.

    :param xml: This can either be a string or a file like object.
    """
    soup = BeautifulSoup(xml, 'xml')

    for row in soup.find_all('row'):
        result = {
            'id': row['id'],
        }
        for cell in row.find_all('cell'):
            name = _extract_name(cell)
            value = cell.text.strip()
            result[name] = value

        yield result


def extract_total(xml):
    """The total count from some XML if available, None otherwise."""
    soup = BeautifulSoup(xml, 'xml')

    rows = soup.find('rows')
    if rows.has_attr('total_count'):
        return int(rows['total_count'])


def _extract_name(cell):
    if cell.has_attr('class'):
        name = cell['class']
    elif cell.has_attr('id'):
        name = cell['id']
    else:
        name = ''
    return name.replace('grid_', '')
