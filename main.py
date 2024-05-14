import flet as ft
from view import *


# Esta función se encarga de crear la página principal de la aplicación y de añadir el control Home a la misma.

def main(page: ft.Page):

    home = Home()

    page.add(home)

ft.app(target=main)