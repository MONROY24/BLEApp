import asyncio
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock
from kivy.uix.popup import Popup
from bleak import BleakClient, BleakScanner, BleakError
import struct


SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
TEMP_CHAR_UUID = "00002a6e-0000-1000-8000-00805f9b34fb"
HUM_CHAR_UUID = "00002a6f-0000-1000-8000-00805f9b34fb"
BLE_DEVICE_NAME = "EnvSensor"

class BLEApp(App):
    def build(self):
        self.client = None
        self.temp_data = []
        self.hum_data = []
        self.current_temp = 0
        self.current_hum = 0

        layout = BoxLayout(orientation='vertical')
        
        header = Label(text="DATOS", font_size='24sp', size_hint_y=None, height=50)
        layout.add_widget(header)
   
        self.graph_temp = Graph(xlabel='Tiempo', ylabel='Temperatura (°C)', x_ticks_minor=5, x_ticks_major=25, y_ticks_major=1, y_grid_label=True, x_grid_label=True, padding=5, xlog=False, ylog=False, x_grid=True, y_grid=True, xmin=0, xmax=100, ymin=-10, ymax=40)
        self.plot_temp = MeshLinePlot(color=[0.5, 1, 0])  
        self.graph_temp.add_plot(self.plot_temp)

        self.graph_hum = Graph(xlabel='Tiempo', ylabel='Humedad (%)', x_ticks_minor=5, x_ticks_major=25, y_ticks_major=10, y_grid_label=True, x_grid_label=True, padding=5, xlog=False, ylog=False, x_grid=True, y_grid=True, xmin=0, xmax=100, ymin=0, ymax=100)
        self.plot_hum = MeshLinePlot(color=[0.5, 1, 0]) 
        self.graph_hum.add_plot(self.plot_hum)

  
        value_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.temp_label = Label(text=f"Temperatura: {self.current_temp} °C", font_size='18sp', size_hint_x=None, width=200)
        self.hum_label = Label(text=f"Humedad: {self.current_hum} %", font_size='18sp', size_hint_x=None, width=200)
        value_layout.add_widget(self.temp_label)
        value_layout.add_widget(self.hum_label)

        layout.add_widget(self.graph_temp)
        layout.add_widget(self.graph_hum)
        layout.add_widget(value_layout)
        
        self.status_label = Label(text="Estado: Desconectado", size_hint_y=None, height=50)
        layout.add_widget(self.status_label)

        button_layout = BoxLayout(size_hint_y=None, height=50)
        self.connect_button = Button(text="Conectar", on_press=self.start_ble_thread)
        button_layout.add_widget(self.connect_button)
        self.reset_button = Button(text="Resetear", on_press=self.reset_data)
        button_layout.add_widget(self.reset_button)
        layout.add_widget(button_layout)
  
        footer = Label(text="© 2024 Humboldt Technology", font_size='12sp', size_hint_y=None, height=30)
        layout.add_widget(footer)
        
        return layout

    def start_ble_thread(self, instance):
        threading.Thread(target=self.run_ble_loop, daemon=True).start()

    def run_ble_loop(self):
        asyncio.run(self.connect_ble())

    async def connect_ble(self):
        try:
            devices = await BleakScanner.discover()
            target_device = None
            for device in devices:
                if device.name == BLE_DEVICE_NAME:
                    target_device = device
                    break

            if not target_device:
                print(f"Dispositivo con nombre {BLE_DEVICE_NAME} no encontrado.")
                self.status_label.text = f"Estado: {BLE_DEVICE_NAME} no encontrado"
                return

            async with BleakClient(target_device, timeout=30.0) as client:
                self.client = client
                self.status_label.text = "Estado: Conectado"

                await client.start_notify(TEMP_CHAR_UUID, self.notification_handler)
                await client.start_notify(HUM_CHAR_UUID, self.notification_handler)

                try:
                    while True:
                        await asyncio.sleep(0.1) 
                except KeyboardInterrupt:
                    await client.stop_notify(TEMP_CHAR_UUID)
                    await client.stop_notify(HUM_CHAR_UUID)
                self.status_label.text = "Estado: Desconectado"
        except BleakError as e:
            print(f"Error de conexión BLE: {e}")
            self.status_label.text = f"Estado: Error de conexión: {e}"
        except asyncio.TimeoutError:
            print("El intento de conexión a BLE se agotó.")
            self.status_label.text = "Estado: Tiempo de conexión agotado"

    def notification_handler(self, sender, data):
        print(f"Notificación recibida de {sender.uuid}: {data}")
        try:
            if len(data) == 4:
                value = struct.unpack('<f', data)[0]
                print(f"Valor desempaquetado de {sender.uuid}: {value}")
                if sender.uuid.lower() == TEMP_CHAR_UUID.lower():
                    self.temp_data.append(value)
                    self.current_temp = value
                    if len(self.temp_data) > 100:
                        self.temp_data.pop(0)
                    print(f"Datos de temperatura: {self.temp_data}")
                    Clock.schedule_once(lambda dt: self.update_graph(self.plot_temp, self.temp_data))
                    Clock.schedule_once(lambda dt: self.update_value_labels())
                    self.check_alert_conditions()
                elif sender.uuid.lower() == HUM_CHAR_UUID.lower():
                    self.hum_data.append(value)
                    self.current_hum = value
                    if len(self.hum_data) > 100:
                        self.hum_data.pop(0)
                    print(f"Datos de humedad: {self.hum_data}")
                    Clock.schedule_once(lambda dt: self.update_graph(self.plot_hum, self.hum_data))
                    Clock.schedule_once(lambda dt: self.update_value_labels())
                    self.check_alert_conditions()
        except struct.error as e:
            print(f"Error al desempaquetar datos: {e}")

    def update_graph(self, plot, data):
        plot.points = [(i, data[i]) for i in range(len(data))]
        print(f"Actualizando gráfica con puntos: {plot.points}")

    def update_value_labels(self, *args):
        self.temp_label.text = f"Temperatura: {self.current_temp:.1f} °C"
        self.hum_label.text = f"Humedad: {self.current_hum:.1f} %"

    def reset_data(self, instance):
        self.temp_data = []
        self.hum_data = []
        self.plot_temp.points = []
        self.plot_hum.points = []
        self.current_temp = 0
        self.current_hum = 0
        self.update_value_labels()

    def show_alert(self, title, message):

        close_button = Button(text="Cerrar", size_hint=(None, None), size=(100, 50))
        close_button.bind(on_press=self.close_popup)

   
        message_label = Label(text=message, size_hint_y=None, height=150, text_size=(400, None), halign='center', valign='middle')


        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(message_label)
        popup_layout.add_widget(close_button)


        popup = Popup(
            title=title,
            content=popup_layout,
            size_hint=(None, None),
            size=(400, 200),
            auto_dismiss=False
        )

        self.current_popup = popup

        
        Clock.schedule_once(lambda dt: popup.open(), 0)

    def close_popup(self, instance):
        if hasattr(self, 'current_popup') and self.current_popup:
            self.current_popup.dismiss()
            self.current_popup = None

    def check_alert_conditions(self):
        if 12 <= self.current_temp <= 18 and self.current_hum > 92:
         
            Clock.schedule_once(lambda dt: self.show_alert("¡Alerta!", "El cultivo está en riesgo de contraer el hongo. Se recomienda aplicar tratamiento."))

    def on_stop(self):
        if self.client:
            asyncio.run(self.client.disconnect())

if __name__ == '__main__':
    BLEApp().run()
















