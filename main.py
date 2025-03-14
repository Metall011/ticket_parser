import tkinter as tk
from tkinter import filedialog, messagebox
from parserTicketPDF import *
import sys

import threading

class RedirectStdout:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, msg):
        self.text_widget.insert(tk.END, msg)
        self.text_widget.yview(tk.END)

    def flush(self):
        pass

def parse_ticket_data():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])

    if not file_path:
        return

    label_file.config(text=f"Выбран файл: {file_path}")
    confirm = messagebox.askyesno("Подтверждение", f"Вы хотите распарсить файл?\n\n{file_path}")

    if confirm:
        try:
            doc_sess = fitz.open(file_path)

            msg_info = 'Выберите папку для сохранения JPG файлов'
            messagebox.showinfo("Выбрать", msg_info)
            path_to_save = filedialog.askdirectory(title=msg_info)

            label_processing.config(text="Подождите, идет обработка...", fg='blue')
            label_processing.update()

            ticket_data = count_seats_per_row(doc_sess)
            show_data(ticket_data)
            from_pdf_to_jpg(doc_sess, ticket_data, path_to_save)

            cnt_pages = count_total_pages(doc_sess)
            cnt_ticket = count_ticket(ticket_data)
            if cnt_pages != cnt_ticket:
                msg_warning = (
                    "Разница в количестве страниц и билетов!\n\n"
                    f"{'Страниц: ' + str(cnt_pages):>20}\n"
                    f"{'Билетов: ' + str(cnt_ticket):>20}"
                )
                messagebox.showwarning("Предупреждение", msg_warning)

            msg_success = 'Файлы успешно сохранены!\n\n'
            for row, data in sorted(ticket_data.items()):
                msg_success += f"Ряд {row}: {data['seats']} мест\n"
            msg_success += f'\nВсего билетов: {cnt_ticket}\n'
            label_processing.config(text="Обработка завершина", fg='green')
            messagebox.showinfo("Готово", msg_success)

        except Exception as e:
            messagebox.showerror('Ошибка', f'Произошла ошибка: {e}')
            label_processing.config(text="Обработка завершина c ошибкой", fg='red')
def parse_ticket_data_async():
    thread = threading.Thread(target=parse_ticket_data)
    thread.start()


def main():
    global label_file, label_processing
    root = tk.Tk()
    root.title('Ticket Parser от DEED')

    window_width = 750
    window_height = 600
    max_wrap_length = window_width
    font_type = 'Courier New'
    font_big = (font_type, 12)
    font_smal = (font_type, 10)

    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    icon_path = "deed.ico"
    root.iconbitmap(icon_path)

    label = tk.Label(root, text='Выберите PDF файл с билетами', font=font_big)
    label.pack(pady=20)
    button = tk.Button(root, text='Выбрать файл', command=parse_ticket_data_async, font=font_big, fg='green')
    button.pack()

    label_file = tk.Label(root, text='Файл не выбран', font=font_smal, wraplength=max_wrap_length)
    label_file.pack(pady=10)

    label_processing = tk.Label(root, text="", font=font_big)
    label_processing.pack(pady=10)


    output_text = tk.Text(root, height=18, width=100, font=font_smal)
    output_text.pack(pady=10)
    sys.stdout = RedirectStdout(output_text)
    print(deed_art + '\nДобро пожаловать в Ticket_Parser от DEED\n')

    exit_button = tk.Button(root, text='Выход', command=root.quit, font=font_big, fg='red')
    exit_button.pack(pady=30)

    root.mainloop()


if __name__ == '__main__':
    main()
