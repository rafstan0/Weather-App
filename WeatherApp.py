import sys
import requests
import logging
import smtplib
from io import BytesIO
from datetime import datetime, timedelta, timezone
from PIL import Image
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog, QHBoxLayout
from PyQt5.QtGui import QIcon, QFont, QPixmap, QImage
from PyQt5.QtCore import Qt

def get_current_weather(city_id):
    api_key = 'd28aab73db8572aae9d8daac9c9b4624'
    base_url = f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_key}&units=metric"

    try:
        response = requests.get(base_url)
        data = response.json()

        if response.status_code == 200:
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind_speed = data["wind"]["speed"]
            weather_icon = data["weather"][0]["icon"]
            country = data["sys"]["country"]
            timezone_offset = data["timezone"]
            return temperature, humidity, pressure, wind_speed, weather_icon, country, timezone_offset
        else:
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None

def get_weekly_forecast(city_id):
    api_key = 'd28aab73db8572aae9d8daac9c9b4624'
    base_url = f"http://api.openweathermap.org/data/2.5/forecast?id={city_id}&appid={api_key}&units=metric"

    try:
        response = requests.get(base_url)
        data = response.json()

        if response.status_code == 200:
            country = data["city"]["country"]
            forecast = {}
            timezone_offset = data["city"]["timezone"]
            for item in data['list']:
                date = item['dt_txt'].split()[0]
                temperature = item['main']['temp']
                humidity = item['main']['humidity']
                pressure = item['main']['pressure']
                wind_speed = item['wind']['speed']
                weather_icon = item['weather'][0]['icon']
                if date not in forecast:
                    forecast[date] = {
                        'temperatures': [temperature],
                        'humidities': [humidity],
                        'pressures': [pressure],
                        'wind_speeds': [wind_speed],
                        'temp_min': temperature,
                        'temp_max': temperature,
                        'weather_icon': weather_icon
                    }
                else:
                    forecast[date]['temperatures'].append(temperature)
                    forecast[date]['humidities'].append(humidity)
                    forecast[date]['pressures'].append(pressure)
                    forecast[date]['wind_speeds'].append(wind_speed)
                    if temperature < forecast[date]['temp_min']:
                        forecast[date]['temp_min'] = temperature
                    if temperature > forecast[date]['temp_max']:
                        forecast[date]['temp_max'] = temperature

            for date, data in forecast.items():
                data['temperature'] = sum(data['temperatures']) / len(data['temperatures'])
                data['humidity'] = sum(data['humidities']) / len(data['humidities'])
                data['pressure'] = sum(data['pressures']) / len(data['pressures'])
                data['wind_speed'] = sum(data['wind_speeds']) / len(data['wind_speeds'])

            return forecast, country, timezone_offset
        else:
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None

def get_hourly_forecast_graph(city_id):
    api_key = 'd28aab73db8572aae9d8daac9c9b4624'
    base_url = f"http://api.openweathermap.org/data/2.5/forecast?id={city_id}&appid={api_key}&units=metric"

    try:
        response = requests.get(base_url)
        data = response.json()

        if response.status_code == 200:
            graph_url = f"http://openweathermap.org/graph?id={city_id}&appid={api_key}"
            return graph_url
        else:
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None

def send_email(recipient, subject, body):
    sender_email = "labprojectgroup102@outlook.pt"
    sender_password = "group102lab"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.office365.com", 587)  # Replace with your SMTP server details
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, message.as_string())
        server.close()
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False

def get_possible_cities(city_name):
    api_key = 'd28aab73db8572aae9d8daac9c9b4624'
    base_url = f"http://api.openweathermap.org/data/2.5/find?q={city_name}&appid={api_key}&units=metric"

    try:
        response = requests.get(base_url)
        data = response.json()

        if response.status_code == 200 and data["count"] > 0:
            return data["list"]
        else:
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Weather Information')
        self.setGeometry(100, 100, 950, 600)
        self.setWindowIcon(QIcon('logo.ico'))
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        self.city_label = QLabel('City Name:')
        self.city_label.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.city_label)

        self.city_input = QLineEdit()
        self.city_input.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.city_input)

        self.current_weather_button = QPushButton('Get Current Weather')
        self.current_weather_button.setFont(QFont('Arial', 12))
        self.current_weather_button.clicked.connect(self.show_current_weather)
        self.layout.addWidget(self.current_weather_button)

        self.weekly_forecast_button = QPushButton('Get Weekly Forecast')
        self.weekly_forecast_button.setFont(QFont('Arial', 12))
        self.weekly_forecast_button.clicked.connect(self.show_weekly_forecast)
        self.layout.addWidget(self.weekly_forecast_button)

        self.weather_display_layout = QVBoxLayout()
        self.weather_display_layout.setAlignment(Qt.AlignCenter)

        self.weather_icon_label = QLabel()
        self.weather_icon_label.setAlignment(Qt.AlignCenter)
        self.weather_display_layout.addWidget(self.weather_icon_label)

        self.weather_info_label = QLabel()
        self.weather_info_label.setAlignment(Qt.AlignCenter)
        self.weather_display_layout.addWidget(self.weather_info_label)

        self.layout.addLayout(self.weather_display_layout)

        self.setLayout(self.layout)
        self.send_email_button = QPushButton('Send Weekly Forecast Email')
        self.send_email_button.setFont(QFont('Arial', 12))
        self.send_email_button.clicked.connect(self.send_weekly_forecast_email)
        self.layout.addWidget(self.send_email_button)

        self.hourly_forecast_button = QPushButton('Get Hourly Forecast Graphic')
        self.hourly_forecast_button.setFont(QFont('Arial', 12))
        self.hourly_forecast_button.clicked.connect(self.show_hourly_forecast_graph)
        self.layout.addWidget(self.hourly_forecast_button)

    def show_current_weather(self):
        try:
            city_name = self.city_input.text()
            possible_cities = get_possible_cities(city_name)
            self.clear_weather_info()  # Clear previous weather info, but keep the input bar and label

            if possible_cities:
                city_dict = {f"{city['name']}, {city['sys']['country']}": city['id'] for city in possible_cities}
                city_list = list(city_dict.keys())

                # Upewnij się, że city_choice jest inicjalizowane
                if len(city_list) > 1:
                    city_choice, ok = QInputDialog.getItem(self, 'Select City', 'Multiple cities found. Please select:',
                                                       city_list, 0, False)
                    if ok and city_choice:
                        selected_city_id = city_dict[city_choice]
                    else:
                        return
                else:
                    city_choice = city_list[0]  # Jeśli jest tylko jedno miasto, przypisz je do city_choice
                    selected_city_id = city_dict[city_choice]

                weather_data = get_current_weather(selected_city_id)
            else:
                QMessageBox.critical(self, 'Error', 'No matching cities found.')
                return

            if weather_data is not None:
                temperature, humidity, pressure, wind_speed, weather_icon, country, timezone_offset = weather_data
                local_time = self.get_local_time(timezone_offset)
                self.display_weather_icon(weather_icon)
                weather_info = f"City: {city_choice}\n"  # Teraz city_choice jest zawsze przypisane
                weather_info += f"Local Time: {local_time.strftime('%H:%M')}\n"
                weather_info += f"Temperature: {temperature}°C\nHumidity: {humidity}%\nPressure: {pressure} hPa\nWind Speed: {wind_speed} m/s"
                self.weather_info_label.setText(weather_info)
            else:
                QMessageBox.critical(self, 'Error', 'Failed to fetch current weather data. Please check the city name.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

    def show_weekly_forecast(self):
        try:
            city_name = self.city_input.text()
            possible_cities = get_possible_cities(city_name)
            self.clear_weather_info()  # Clear previous weather info, but keep the input bar and label

            if possible_cities:
                city_dict = {f"{city['name']}, {city['sys']['country']}": city['id'] for city in possible_cities}
                city_list = list(city_dict.keys())

                if len(city_list) > 1:
                    city_choice, ok = QInputDialog.getItem(self, 'Select City', 'Multiple cities found. Please select:',
                                                           city_list, 0, False)
                    if ok and city_choice:
                        selected_city_id = city_dict[city_choice]
                        forecast_data = get_weekly_forecast(selected_city_id)
                    else:
                        return
                else:
                    selected_city_id = city_dict[city_list[0]]
                    forecast_data = get_weekly_forecast(selected_city_id)
            else:
                QMessageBox.critical(self, 'Error', 'No matching cities found.')
                return

            if forecast_data is not None:
                forecast, country, timezone_offset = forecast_data
                forecast_widget = QWidget()
                forecast_layout = QHBoxLayout()

                for date, data in forecast.items():
                    day_widget = QWidget()
                    day_layout = QVBoxLayout()
                    date_info = QLabel(f"Date: {date}\n")
                    temp_info = QLabel(f"Temperature: Max {data['temp_max']}°C, Min {data['temp_min']}°C\n")
                    avg_temp_info = QLabel(f"Average Temperature: {data['temperature']:.2f}°C\n")
                    humidity_info = QLabel(f"Humidity: {data['humidity']:.2f}%\n")
                    pressure_info = QLabel(f"Pressure: {data['pressure']:.2f} hPa\n")
                    wind_speed_info = QLabel(f"Average Wind Speed: {data['wind_speed']:.2f} m/s\n\n")

                    day_layout.addWidget(date_info)
                    day_layout.addWidget(temp_info)
                    day_layout.addWidget(avg_temp_info)
                    day_layout.addWidget(humidity_info)
                    day_layout.addWidget(pressure_info)
                    day_layout.addWidget(wind_speed_info)

                    icon_label = QLabel()
                    icon_url = f"http://openweathermap.org/img/wn/{data['weather_icon']}@2x.png"
                    response = requests.get(icon_url)
                    if response.status_code == 200:
                        image = Image.open(BytesIO(response.content))
                        image = image.resize((80, 80), Image.LANCZOS)
                        image = image.convert("RGBA")

                        data = image.tobytes("raw", "RGBA")
                        qim = QImage(data, image.size[0], image.size[1], QImage.Format_RGBA8888)

                        pixmap = QPixmap.fromImage(qim)
                        icon_label.setPixmap(pixmap)
                    else:
                        icon_label.setText("No icon")

                    icon_label.setAlignment(Qt.AlignCenter)
                    day_layout.addWidget(icon_label)

                    day_widget.setLayout(day_layout)
                    forecast_layout.addWidget(day_widget)

                forecast_widget.setLayout(forecast_layout)
                self.layout.addWidget(forecast_widget)
            else:
                QMessageBox.critical(self, 'Error', 'Failed to fetch weekly forecast data. Please check the city name.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

    def send_weekly_forecast_email(self):
        try:
            city_name = self.city_input.text()
            possible_cities = get_possible_cities(city_name)

            if possible_cities:
                city_dict = {f"{city['name']}, {city['sys']['country']}": city['id'] for city in possible_cities}
                city_list = list(city_dict.keys())

                if len(city_list) > 1:
                    city_choice, ok = QInputDialog.getItem(self, 'Select City', 'Multiple cities found. Please select:',
                                                           city_list, 0, False)
                    if ok and city_choice:
                        selected_city_id = city_dict[city_choice]
                        forecast_data = get_weekly_forecast(selected_city_id)
                    else:
                        return
                else:
                    selected_city_id = city_dict[city_list[0]]
                    forecast_data = get_weekly_forecast(selected_city_id)
            else:
                QMessageBox.critical(self, 'Error', 'No matching cities found.')
                return

            if forecast_data is not None:
                forecast, country, timezone_offset = forecast_data
                email, ok = QInputDialog.getText(self, 'Email Address', 'Enter the recipient\'s email address:')
                if ok and email:
                    body = f"Here’s the weather forecast for {city_choice} for the next week:\n\n"
                    for date, data in forecast.items():
                        body += f"Date: {date}\n"
                        body += f"Temperature: Max {data['temp_max']}°C, Min {data['temp_min']}°C\n"
                        body += f"Average Temperature: {data['temperature']:.2f}°C\n"
                        body += f"Humidity: {data['humidity']:.2f}%\n"
                        body += f"Pressure: {data['pressure']:.2f} hPa\n"
                        body += f"Average Wind Speed: {data['wind_speed']:.2f} m/s\n\n"

                    success = send_email(email, "Weekly Forecast", body)
                    if success:
                        QMessageBox.information(self, "Success", "Email sent successfully!")
                    else:
                        QMessageBox.critical(self, "Error", "Failed to send email. Please try again.")
            else:
                QMessageBox.critical(self, 'Error', 'Failed to fetch weekly forecast data. Please check the city name.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

    def show_hourly_forecast_graph(self):
        try:
            city_name = self.city_input.text()
            possible_cities = get_possible_cities(city_name)
            self.clear_weather_info()  # Clear previous weather info, but keep the input bar and label

            if possible_cities:
                city_dict = {f"{city['name']}, {city['sys']['country']}": city['id'] for city in possible_cities}
                city_list = list(city_dict.keys())

                if len(city_list) > 1:
                    city_choice, ok = QInputDialog.getItem(self, 'Select City', 'Multiple cities found. Please select:',
                                                           city_list, 0, False)
                    if ok and city_choice:
                        selected_city_id = city_dict[city_choice]
                        graph_url = get_hourly_forecast_graph(selected_city_id)
                    else:
                        return
                else:
                    selected_city_id = city_dict[city_list[0]]
                    graph_url = get_hourly_forecast_graph(selected_city_id)
            else:
                QMessageBox.critical(self, 'Error', 'No matching cities found.')
                return

            if graph_url is not None:
                graph_label = QLabel()
                response = requests.get(graph_url)
                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    image = image.convert("RGBA")

                    data = image.tobytes("raw", "RGBA")
                    qim = QImage(data, image.size[0], image.size[1], QImage.Format_RGBA8888)

                    pixmap = QPixmap.fromImage(qim)
                    graph_label.setPixmap(pixmap)
                else:
                    graph_label.setText("Failed to load graph")
                    logging.error(f"Failed to load graph. HTTP Status code: {response.status_code}")

                self.layout.addWidget(graph_label)
            else:
                QMessageBox.critical(self, 'Error', 'Failed to fetch hourly forecast graphic.')
        except Exception as e:
            logging.error(f"An error occurred while fetching the hourly forecast graph: {e}")
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')
    def get_local_time(self, timezone_offset):
        local_time = datetime.now(timezone.utc) + timedelta(seconds=timezone_offset)
        return local_time

    def display_weather_icon(self, weather_icon):
        icon_url = f"http://openweathermap.org/img/wn/{weather_icon}@2x.png"
        response = requests.get(icon_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image = image.resize((80, 80), Image.LANCZOS)
            image = image.convert("RGBA")

            data = image.tobytes("raw", "RGBA")
            qim = QImage(data, image.size[0], image.size[1], QImage.Format_RGBA8888)

            pixmap = QPixmap.fromImage(qim)
            self.weather_icon_label.setPixmap(pixmap)
        else:
            QMessageBox.critical(self, 'Error', 'Failed to load weather icon.')

    def clear_weather_info(self):
        self.weather_icon_label.clear()
        self.weather_info_label.clear()
        while self.layout.count() > 6:  # Keeping the first six static widgets
            item = self.layout.takeAt(6)
            if item.widget() is not None:
                item.widget().deleteLater()
            elif item.layout() is not None:
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                    elif sub_item.layout():
                        while sub_item.layout().count():
                            sub_sub_item = sub_item.layout().takeAt(0)
                            if sub_sub_item.widget():
                                sub_sub_item.widget().deleteLater()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(
        "QPushButton { color: black; background-color: #007BFF; border: 1px solid #1055cc; border-radius: 4px; padding: 5px; }"
        "QLineEdit { padding: 5px; border: 1px solid #ccc; border-radius: 4px; font-size: 15px; }"
        "QLabel { font-size:18px; background-color: #ffffff; margin: 0px; }"  
        "QWidget { background-color: #d0d0e1; }"
        "QMessageBox QPushButton { background-color: #007BFF; color: black; }")
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
