import flet as ft
import subprocess
import os

def run_app_py(search_type):
    try:
        # Mapeo de la opción seleccionada con el script correspondiente y los argumentos necesarios
        search_type_map = {
            "Búsqueda por Anchura": ("app.py", "anchura"),
            "Búsqueda por Profundidad": ("Profundidad.py", "profundidad"),
            "Búsqueda por Profundidad Iterativa": ("ProfundidadIterativa.py", "profundidad_iterativa"),
            "Búsqueda Bidireccional": ("bidireccional.py", "bidireccional"),
        }

        # Obtener el nombre del script y el argumento correspondiente
        script_name, search_type_argument = search_type_map.get(search_type, ("app.py", "anchura"))

        # Especificar la ruta completa de la carpeta donde se encuentran los scripts
        script_path = os.path.join("C:/Users/moyol/OneDrive/Documentos/IA/BusquedasNoInformadas/IAbusqueda", script_name)

        # Verificar si el archivo existe antes de ejecutarlo
        if not os.path.isfile(script_path):
            return f"Error: No se encontró el archivo {script_path}"

        # Ejecutar el script correspondiente con el argumento del tipo de búsqueda
        result = subprocess.run(
            ['python', script_path, search_type_argument],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error ejecutando {script_name}: {e.stderr}"

def main(page: ft.Page):
    page.title = "Interfaz de Ovejas y Lobos"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    menu = ft.Dropdown(
        options=[
            ft.dropdown.Option("Búsqueda por Anchura"),
            ft.dropdown.Option("Búsqueda por Profundidad"),
            ft.dropdown.Option("Búsqueda por Profundidad Iterativa"),
            ft.dropdown.Option("Búsqueda Bidireccional"),
        ],
        width=200,
    )

    panel_menu = ft.Container(
        content=ft.Column(
            controls=[menu],
        ),
        width=220,
        bgcolor="wine",
        padding=10
    )

    list_view = ft.ListView(
        width=page.window.width - 220,
        height=page.window.height,
        spacing=10,
        padding=10,
        auto_scroll=True
    )

    def on_menu_change(e):
        search_type = menu.value
        if search_type:
            # Ejecutar el script correspondiente y obtener la salida
            output = run_app_py(search_type)
            # Agregar los resultados al ListView sin eliminar los anteriores
            list_view.controls.append(ft.Text(f"Resultados de {search_type}:", color="white"))
            list_view.controls.append(ft.Text(output, color="white"))
            page.update()

    menu.on_change = on_menu_change

    page.add(
        ft.Row(
            controls=[panel_menu, list_view],
            alignment=ft.MainAxisAlignment.START,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
