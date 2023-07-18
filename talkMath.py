import sys
import speech_recognition as sr
import pyttsx3
from num2words import num2words
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def process_command(command):
    words = command.split()
    if len(words) < 3:
        return "Anlayamadım, lütfen tekrarlar mısınız?"

    try:
        num1 = float(words[0])
        operator = words[1]
        num2 = float(words[2])
    except ValueError:
        return "Sayıları anlayamadım, lütfen geçerli sayılar söyleyiniz."

    if operator in ["artı", "+"]:
        result = num1 + num2

    elif operator in ["eksi", "-"]:
        result = num1 - num2

    elif operator in ["çarpı", "*", "kere", "kez"]:
        result = num1 * num2

    elif operator in ["bölü", "/"]:
        if num2 == 0:
            return "Bir sayıyı sıfıra bölemezsiniz."
        result = num1 / num2

    else:
        return "Anlayamadım, lütfen tekrarlar mısınız?"
    
    return int(result)

class HoverLabel(QLabel):
    def __init__(self, *args, **kwargs):
        QLabel.__init__(self, *args, **kwargs)
        self.original_style = """
            QLabel {
                background-color: #FFA500;
                font-size: 75px;
                color: #FFDAB9;
                border-radius: 15px;
            }
        """
        self.hover_style = """
            QLabel {
                background-color: #FFFDD0;
                font-size: 75px;
                color: #FFA500;
                border-radius: 15px;
            }
        """
        self.setStyleSheet(self.original_style)

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_style)

    def leaveEvent(self, event):
        self.setStyleSheet(self.original_style)


class CalculatorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TalkMath")
        self.resize_to_screen()

        layout = QVBoxLayout()

        self.label = HoverLabel("Lütfen 'HESAPLA' Butonuna Tıklayıp \n İşleminizi Söyleyiniz...", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.button_layout = QHBoxLayout()
        self.calculate_btn = QPushButton("HESAPLA", self)
        self.calculate_btn.clicked.connect(self.listen_for_command)
        self.calculate_btn.setFixedSize(550, 400)
        self.calculate_btn.setStyleSheet("""
        QPushButton {
            background-color: #FFFDD0; 
            font-size: 70px; 
            color: #FFA500; 
            border-radius: 15px;
        }
        QPushButton:hover {
            background-color: #FFA500; 
            color: #FFFDD0;
        }""")
        self.button_layout.addWidget(self.calculate_btn)

        self.show_results_btn = QPushButton("SONUÇLARI GÖSTER", self)
        self.show_results_btn.clicked.connect(self.show_results)
        self.show_results_btn.setFixedSize(780, 400)
        self.show_results_btn.setStyleSheet("""
        QPushButton {
            background-color: #FFFDD0; 
            font-size: 70px; 
            color: #FFA500; 
            border-radius: 15px;
        }
        QPushButton:hover {
            background-color: #FFA500; 
            color: #FFFDD0;
        }""")
        self.button_layout.addWidget(self.show_results_btn)

        self.add_exit_button()

        layout.addLayout(self.button_layout)
        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background-color: #FFDAB9;")
        self.setCentralWidget(container)

        self.results = []

    def resize_to_screen(self):
        screen = QApplication.desktop().screenGeometry()
        self.setGeometry(screen)

    def add_exit_button(self):
        self.exit_btn = QPushButton("ÇIKIŞ", self)
        self.exit_btn.clicked.connect(self.exit_app)
        self.exit_btn.setFixedSize(550, 400)
        self.exit_btn.setStyleSheet("""
        QPushButton {
            background-color: #FFFDD0; 
            font-size: 70px; 
            color: #FFA500; 
            border-radius: 15px;
        }
        QPushButton:hover {
            background-color: #FF0000; 
            color: #FFFDD0;
        }""")
        self.button_layout.addWidget(self.exit_btn)

    def listen_for_command(self):
        self.label.setText("SİZİ DİNLİYORUM...")
        self.label.setVisible(True)
        self.calculate_btn.setVisible(False)
        self.show_results_btn.setVisible(False)
        self.exit_btn.setVisible(False)  # Butonu gizle
        QApplication.processEvents()
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source)

        # İşlem bittiğinde butonu tekrar göster
        self.exit_btn.setVisible(True)
        self.calculate_btn.setVisible(True)
        self.show_results_btn.setVisible(True)

        try:
            command = r.recognize_google(audio, language='tr-TR').lower()

            response = process_command(command)

            speak(num2words(response, lang='tr'))

            self.results.append(response)
            self.label.setText(str(response))

        except sr.UnknownValueError:
            print("Anlayamadım, lütfen tekrarlar mısınız?")
            speak("Anlayamadım, lütfen tekrarlar mısınız?")

        except sr.RequestError as e:
            print(f"Ses Tanıma Servisi Hatası: {e}")
            speak(f"Ses Tanıma Servisi Hatası: {e}")

    def show_results(self):
        if self.results:
            result_text = "Geçmiş Sonuçlar:\n" + "\n".join(map(str, self.results))
        else:
            result_text = "Henüz Yapılan İşlem Yok!"
        self.label.setText(result_text)

    def exit_app(self):
        button_reply = QMessageBox.question(self, 'ÇIKIŞ YAP', "Çıkmak istediğinizden emin misiniz?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if button_reply == QMessageBox.Yes:
            print('Çıkış Yapılıyor...')
            sys.exit()
        else:
            pass

def main():
    app = QApplication(sys.argv)

    main_win = CalculatorApp()
    main_win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
