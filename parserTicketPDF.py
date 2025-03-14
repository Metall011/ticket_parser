import os
import fitz  # PyMuPDF
import re
from collections import defaultdict
from PIL import Image
from intro_deed import deed_art


def extract_row_number(text):
    match = re.search(r'Ряд\s*(\d+)', text, re.IGNORECASE)
    return int(match.group(1)) if match else None

def extract_seat_number(text):
    match = re.search(r'Место\s*(\d+)', text, re.IGNORECASE)
    return int(match.group(1)) if match else None

def count_total_pages(doc_sess):
    total_pages = len(doc_sess)
    print(f"Общее количество страниц в PDF: {total_pages}")
    return total_pages

def count_ticket(ticket_data):
    page_cnt = sum(len(data['page_and_seat']) for data in ticket_data.values())
    print(f'Количество обработанных билетов: {page_cnt}')
    return page_cnt

def show_data(ticket_data):
    print('Количество мест в каждом ряду и их страницы:')
    for row, data in sorted(ticket_data.items()):
        print(f"Ряд {row}: {data['seats']} мест, страницы и места: {data['page_and_seat']}")
    print()

def find_pdf_file():
    print('Найденные PDF файлы: ')
    for file_name in os.listdir():
        if file_name.endswith('.pdf'):
            print(file_name)

def count_seats_per_row(doc_sess):
    ticket_data = defaultdict(lambda: {'seats': 0, 'page_and_seat': []})
    for page_num, page in enumerate(doc_sess, start=1):
        text = page.get_text("text")
        row = extract_row_number(text)
        seat = extract_seat_number(text)
        if row is not None:
            ticket_data[row]['seats'] += 1
            ticket_data[row]['page_and_seat'].append((page_num, seat))
    return ticket_data

def from_pdf_to_jpg(doc_sess, ticket_data, path_to_save=''):
    path_to_save = os.path.join(path_to_save, 'output_jpg')
    os.makedirs(path_to_save, exist_ok=True)

    for row, data in ticket_data.items():
        row_folder = os.path.join(path_to_save, f"Ряд {row} (мест {data['seats']})")
        os.makedirs(row_folder, exist_ok=True)

        for page_num, seat in data['page_and_seat']:
            page = doc_sess.load_page(page_num - 1)
            pix = page.get_pixmap()
            img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            img_name = f'Ряд {row}, Место {seat} (стр {page_num}).jpg'
            img_path = os.path.join(row_folder, img_name)
            img.save(img_path, 'JPEG')
            print(f'Сохранено в {row_folder}, название: {img_name}')

    print(f"Все страницы будут сохранены в {path_to_save}\n")

if __name__ == '__main__':
    try:
        print(deed_art)
        print('Добро пожаловать в Ticket_Parser от DEED\n')

        find_pdf_file()
        pdf_path = input('\nВведите название PDF файла: ')
        doc_sess = fitz.open(pdf_path)
        ticket_data = count_seats_per_row(doc_sess)
        show_data(ticket_data)
        from_pdf_to_jpg(doc_sess, ticket_data)

        if count_total_pages(doc_sess) != count_ticket(ticket_data):
            print('! ВНИМАНИЕ РАЗНИЦА В ИТОГАХ !')

        input('Для выхода и сохранения нажмите ENTER')

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        input('Для выхода нажмите ENTER')
        raise
