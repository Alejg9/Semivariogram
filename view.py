import flet as ft
from calculations.variance import *
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flet.plotly_chart import PlotlyChart


# Define la clase Home, que hereda de UserControl
class Home(ft.UserControl):

    # Define el método build, que se encarga de construir la página principal de la aplicación
    def build(self):
        # Declaramos los objetos que vamos a utilizar en la página

        self.chart = PlotlyChart(expand=True)

        self.x = self.Input("X", 100)
        self.y = self.Input("Y", 100)
        self.az = self.Input("Azimut", 45)
        self.tolerance = self.Input("Ángulo de tolerancia", 20)
        self.wb = self.Input("Ancho de banda", 10)
        self.lag = self.Input("Lag", 10)
        self.lags = self.Input("Número de lags", 10)

        # Creamos una instancia de la clase Grid, que se encarga de manejar los datos de la grilla

        self.grid = Grid(self.x.value, self.y.value)

        # A través del método drawCone, generamos la figura inicial de la grilla

        fig = self.grid.drawCone(
            self.lag.value,
            self.lags.value,
            self.wb.value,
            self.az.value,
            self.tolerance.value
        )

        # Asignamos la figura al chart
        self.chart.figure = fig

        # Creamos una instancia de la clase FilePicker, que se encarga de manejar la carga de archivos
        self.file_picker = ft.FilePicker(on_result=lambda e: self.files(e))

        # Creamos un botón para cargar los datos
        file_picker = ft.ElevatedButton(
            "Cargar datos",
            on_click=lambda e: self.file_picker.pick_files(allow_multiple=False),
        )

        # Creamos el control principal de la página, dentro del cual incluimos los controles de entrada y el chart
        self.root_control = ft.Row(
            height=800,
            controls=[
                ft.Column(  # Columna con los controles de entrada
                    width=200,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        ft.Row(
                            controls=[
                                InputAndLabel("X:", self.x),
                                InputAndLabel("Y:", self.y),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        file_picker,
                        InputAndLabel("Azimut:", self.az),
                        InputAndLabel("Ángulo de tolerancia:", self.tolerance),
                        InputAndLabel("Ancho de banda:", self.wb),
                        InputAndLabel("Lag:", self.lag),
                        InputAndLabel("Número de lags:", self.lags),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    "Calcular varianza",
                                    on_click=lambda e: self.variogam(),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        self.file_picker,  # Add file_picker to the page
                    ],
                ),
                ft.Row( # Fila que contiene el chart
                    controls=[
                        ft.Column(
                            controls=[
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    width=1000,
                ),
            ],
        )

        # Añadimos el chart al control principal
        self.root_control.controls[1].controls[0].controls.append(self.chart)

        # Retornamos el control principal
        return self.root_control

    # Método que se encarga de cargar los datos del archivo
    def files(self, e):
        # Si no hay archivos, no hacemos nada
        if not e.files:
            return
        
        # Obtenemos el nombre y la ruta del archivo
        name = e.files[0].name
        path = e.files[0].path

        # Obtenemos la extensión del archivo
        extension = name.split(".")[-1]

        # Si la extensión es txt, csv o xlsx, leemos el archivo y lo guardamos en un DataFrame en caso contrario terminamos la funcion
        if extension == 'txt':
            df = pd.read_csv(path, sep='\t')
        elif extension == 'csv':
            df = pd.read_csv(path)
        elif extension == 'xlsx':
            df = pd.read_excel(path)
        else:
            return 
        
        # Obtenemos las columnas x, y y por del DataFrame para guardarlo en la grilla y dibujar el cono con los datos cargados
        x = df["x"]
        y = df["y"]
        z = df["por"]

        self.grid = Grid(self.x.value, self.y.value)

        self.grid.addData(x, y, z)
            
        self.chart.figure = self.grid.drawCone(
            self.lag.value,
            self.lags.value,
            self.wb.value,
            self.az.value,
            self.tolerance.value
        )

        self.chart.update()

    # Método que se encarga de crear un control de entrada   
    def Input(self, placeholder:str, default):
        output = ft.CupertinoTextField(
                placeholder_text=placeholder,
                input_filter=ft.InputFilter(allow=True, regex_string=r"[0.0-9.0]", replacement_string=""),
                width=50,
                value=default,
                on_blur=lambda e: self.update_grid_fig(e), # Cuando se pierde el foco del input, se actualiza el cono
            )
        
        return output
    
    # Método que se encarga de actualizar el cono
    def update_grid_fig(self, e):
        # Redibujamos el cono con los nuevos valores de los inputs
        self.chart.figure = self.grid.drawCone(
            self.lag.value,
            self.lags.value,
            self.wb.value,
            self.az.value,
            self.tolerance.value
        )
        

        self.chart.update()

    def variogam(self):
        # Calculamos el variograma y lo dibujamos
        fig = self.grid.drawVariogram()

        self.chart.figure = fig

        self.chart.update()

# Creamos una función que nos retorne un control de entrada y una etiqueta
def InputAndLabel(label: str, child: ft.CupertinoTextField):
    output = ft.Row(
        controls=[
            ft.Text(label),
            child,
        ],
        alignment=ft.MainAxisAlignment.END,
    )

    return output


