# BLEApp - Aplicación de Monitoreo de Temperatura y Humedad vía Bluetooth LE

Esta aplicación Kivy está diseñada para recibir y visualizar datos de temperatura y humedad enviados desde un dispositivo Bluetooth Low Energy (BLE). Utiliza la biblioteca `bleak` para la comunicación BLE y `kivy_garden.graph` para mostrar los datos en gráficos.

## Características

* **Comunicación BLE:** Se conecta a un dispositivo BLE específico ("EnvSensor") y recibe datos de temperatura y humedad.
* **Visualización Gráfica:** Muestra los datos de temperatura y humedad en gráficos actualizados en tiempo real.
* **Interfaz de Usuario Kivy:** Proporciona una interfaz gráfica para mostrar los datos y el estado de la conexión.
* **Alertas:** Implementa un sistema de alertas mediante popups para notificar condiciones específicas (riesgo de hongos).
* **Manejo de Datos:** Almacena y actualiza los datos de temperatura y humedad, y permite resetearlos.

## Requisitos

* **Python 3.x**
* **Kivy:** Framework de Python para el desarrollo de interfaces de usuario.
* **bleak:** Biblioteca de Python para la comunicación Bluetooth Low Energy.
    ```bash
    pip install bleak
    ```
* **kivy\_garden.graph:** Widget de Kivy Garden para la generación de gráficos.
    ```bash
    garden install graph
    ```

* **Dispositivo BLE Emisor:** Un dispositivo (e.g., Arduino Nano 33 BLE Sense) que transmite datos de temperatura y humedad a través de BLE. Debe configurarse para:
    * Anunciar el nombre "EnvSensor".
    * Exponer servicios y características BLE con UUIDs específicos (`SERVICE_UUID`, `TEMP_CHAR_UUID`, `HUM_CHAR_UUID`).
    * Enviar datos como valores float empaquetados en formato little-endian (`<f`).

## Instalación

1.  **Instalar Python:** Asegúrate de tener Python 3.x instalado.

2.  **Instalar Kivy:**
    ```bash
    pip install kivy
    ```

3.  **Instalar bleak:**
    ```bash
    pip install bleak
    ```

4.  **Instalar kivy\_garden.graph:**
    ```bash
    garden install graph
    ```

## Uso

1.  **Ejecutar la Aplicación:**
    ```bash
    python tu_archivo_kivy.py
    ```
    (Reemplaza `tu_archivo_kivy.py` con el nombre de tu archivo Python).

2.  **Interfaz de la Aplicación:**
    * La aplicación muestra una interfaz con gráficos de temperatura y humedad, etiquetas para los valores actuales y un botón para conectar/desconectar.

3.  **Conexión BLE:**
    * Al iniciar, la aplicación busca un dispositivo BLE con el nombre "EnvSensor".
    * Al presionar el botón "Conectar", se inicia el proceso de conexión.
    * El estado de la conexión se muestra en la etiqueta de estado.

4.  **Recepción y Visualización de Datos:**
    * Una vez conectado, la aplicación recibe datos de temperatura y humedad.
    * Los valores se actualizan en las etiquetas de temperatura y humedad.
    * Los gráficos se actualizan en tiempo real para mostrar la evolución de los datos.

5.  **Alertas:**
    * Si la temperatura está entre 12°C y 18°C y la humedad es superior al 92%, se muestra una alerta en un popup indicando riesgo de hongos.

6.  **Resetear Datos:**
    * El botón "Resetear" limpia los datos y los gráficos.

## Explicación del Código

El código define una aplicación Kivy (`BLEApp`) que:

* **Configuración BLE:** Define los UUIDs para el servicio y las características de temperatura y humedad, así como el nombre del dispositivo BLE objetivo.
* **Interfaz de Usuario:** Crea la interfaz de usuario con Kivy, incluyendo gráficos (`Graph`, `MeshLinePlot`), etiquetas (`Label`), botones (`Button`) y un popup para las alertas.
* **Conexión BLE:**
    * Utiliza `bleak` para escanear dispositivos BLE y conectarse al dispositivo "EnvSensor".
    * Inicia notificaciones para las características de temperatura y humedad.
    * Maneja errores de conexión y timeouts.
* **Recepción de Datos:**
    * La función `notification_handler` se llama cuando se reciben datos de las características BLE.
    * Los datos (en formato bytes) se desempaquetan como floats usando `struct.unpack('<f', data)[0]`.
    * Los valores de temperatura y humedad se actualizan y se agregan a las listas de datos.
* **Actualización de Gráficos:**
    * La función `update_graph` actualiza los puntos de los gráficos con los nuevos datos.
    * Se utiliza `Clock.schedule_once` para actualizar la interfaz de usuario desde el hilo de eventos de Kivy.
* **Alertas:**
    * La función `check_alert_conditions` verifica si se cumplen las condiciones de alerta y muestra un popup si es necesario.
* **Manejo de Hilos:**
    * Se utiliza `threading` para ejecutar el bucle BLE en un hilo separado para evitar bloquear el hilo principal de la interfaz de usuario.
    * `asyncio.run` se usa para ejecutar la corrutina `connect_ble` en el hilo.

## Notas Importantes

* **UUIDs y Nombre del Dispositivo:** Asegúrate de que los UUIDs (`SERVICE_UUID`, `TEMP_CHAR_UUID`, `HUM_CHAR_UUID`) y el nombre del dispositivo (`BLE_DEVICE_NAME`) en el código de Python coincidan exactamente con la configuración en tu dispositivo BLE emisor.
* **Formato de Datos:** El código espera que el dispositivo BLE emisor envíe los datos de temperatura y humedad como valores float de 4 bytes, empaquetados en formato little-endian.
* **Manejo de Errores:** El código incluye un manejo básico de errores, pero se puede mejorar para hacerlo más robusto.
* **Rendimiento:** Para mejorar el rendimiento, especialmente con altas tasas de datos, considera optimizar la forma en que se actualizan los gráficos y se manejan los datos.
* **Dependencias:** Asegúrate de instalar todas las dependencias necesarias.
