import csv
import glob
import os


class PriceMachine:

    def __init__(self):
        self.data = []
        self.name_length = 30  # Устанавливаем максимальную длину названия товара

    def load_prices(self, file_path='./'):
        # Сканируем каталог и находим файлы с нужным именем
        global files
        try:
            files = glob.glob(file_path + '*price*.csv')
        except ValueError:
            print('Не найдены файлы содержащих слово "price" и имеющие разширение csv')

        # Открываем поочередно файлы
        for file in files:
            with open(file, newline='', encoding='utf-8') as csvfile:
                oper = csv.reader(csvfile, delimiter=',')
                headers = next(oper)
                product_column, price_column, weight_column = self._search_product_price_weight(headers)

                #   Проверяем соответствие заголовков в открытом файле. Если все соответствует,
                #   то добавляем значения в список. Если есть несоответствия, то выдаем ошибку.
                for row in oper:
                    if row[product_column] and row[price_column] and row[weight_column]:
                        product_name = row[product_column].strip()
                        try:
                            price = float(row[price_column].strip())
                            weight = float(row[weight_column].strip())
                            price_kg = price / weight

                            self.data.append({
                                'название': product_name,
                                'цена': price,
                                'масса': weight,
                                'файл': file,
                                'цена за кг': price_kg
                            })
                        except ValueError:
                            print(f"Ошибка преобразования значения в строке файла {file}: {row}")

    def _search_product_price_weight(self, headers):
        """
        Возвращает индексы столбцов с названием товара, ценой и весом.
        """
        product_columns = ['название', 'продукт', 'товар', 'наименование']
        price_columns = ['цена', 'розница']
        weight_columns = ['фасовка', 'масса', 'вес']

        product_column = next(i for i, h in enumerate(headers) if h.lower() in product_columns)
        price_column = next(i for i, h in enumerate(headers) if h.lower() in price_columns)
        weight_column = next(i for i, h in enumerate(headers) if h.lower() in weight_columns)

        return product_column, price_column, weight_column

    def export_to_html(self, fname='output.html'):
        """
        Экспортирует данные в HTML-файл.
        """
        Full_list = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th><th>Название</th><th>Цена</th><th>Фасовка</th><th>Файл</th><th>Цена за кг.</th>
                </tr>
        '''

        for idx, item in enumerate(sorted(self.data, key=lambda x: x['цена за кг'])):
            Full_list += f'''
                        <tr>
                            <td>{idx + 1}</td><td>{item['название']}</td><td>{item['цена']:.2f}</td><td>{item['масса']:.2f}</td><td>{os.path.basename(item['файл'])}</td><td>{item['цена за кг']:.2f}</td>
                        </tr>
                    '''
        Full_list += '''
                    </table>
                </body>
                </html>
                '''
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(Full_list)

    def find_text(self, search_text: str):
        """
        Поиск товаров по частичному совпадению названия.
        """
        results = [
            item for item in self.data
            if search_text.lower() in item['название'].lower()
        ]

        return sorted(results, key=lambda x: x['цена за кг'])


# Основной блок программы
if __name__ == "__main__":
    pm = PriceMachine()
    pm.load_prices('./')

    while True:
        user_input = input("Введите текст для поиска или 'exit' для завершения: ").strip().lower()

        if user_input == 'exit':
            print("Работа завершена.")
            pm.export_to_html()
            break

        results = pm.find_text(user_input)

        if results:
            for i, result in enumerate(results, start=1):
                print(
                    f"{i:>3}. {result['название'][:pm.name_length]:<{pm.name_length}} {result['цена']:>10.2f} {result['масса']:>5.2f} {os.path.basename(result['файл']):<20} {result['цена за кг']:>10.2f}")
        else:
            print("Товары не найдены.")
