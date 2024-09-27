import flet as ft
import subprocess
import os

def run_app_py(search_type):
    try:
        # Mapeo de la opción seleccionada con el script correspondiente y los argumentos necesarios
        search_type_map = {
            "Búsqueda por Anchura": ("anchura.py", "anchura", "anchura.png"),
            "Búsqueda por Profundidad": ("Profundidad.py", "profundidad", "profundidad.png"),
            "Búsqueda por Profundidad Iterativa": ("ProfundidadIterativa.py", "profundidad_iterativa", "iterativa.png"),
            "Búsqueda Bidireccional": ("bidireccional.py", "bidireccional", "bidireccional.png"),
        }

        # Obtener el nombre del script y el argumento correspondiente
        script_name, search_type_argument, image_name = search_type_map.get(search_type, ("anchura.py", "anchura", "anchura.png"))

        # Especificar la ruta completa de la carpeta donde se encuentran los scripts
        script_path = os.path.join("C:\\Users\\Personal\\Desktop\\IA_OvejasyLobos", script_name)

        # Verificar si el archivo existe antes de ejecutarlo
        if not os.path.isfile(script_path):
            return "", f"Error: No se encontró el archivo {script_path}"

        # Ejecutar el script correspondiente con el argumento del tipo de búsqueda
        result = subprocess.run(
            ['python', script_path, search_type_argument],
            capture_output=True, text=True, check=True
        )

        # Ruta completa de la imagen generada
        image_path = os.path.join("C:\\Users\\Personal\\Desktop\\IA_OvejasyLobos", image_name)

        return result.stdout, image_path  # Devuelve la salida del script y la ruta de la imagen
    except subprocess.CalledProcessError as e:
        return "", f"Error ejecutando {script_name}: {e.stderr}"

def main(page: ft.Page):
    page.title = "Interfaz de Ovejas y Lobos"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Variables para zoom
    zoom_level = 1.0

    # Dropdown para seleccionar tipo de búsqueda
    menu = ft.Dropdown(
        options=[
            ft.dropdown.Option("Búsqueda por Anchura"),
            ft.dropdown.Option("Búsqueda por Profundidad"),
            ft.dropdown.Option("Búsqueda por Profundidad Iterativa"),
            ft.dropdown.Option("Búsqueda Bidireccional"),
        ],
        width=200,
    )

    # Panel lateral para el menú
    panel_menu = ft.Container(
        content=ft.Column(
            controls=[menu],
        ),
        width=220,
        bgcolor="wine",
        padding=10
    )

    # Área de resultados y visualización de imágenes
    list_view = ft.ListView(
        width=page.window.width - 220,
        height=page.window.height - 350,
        spacing=10,
        padding=10,
        auto_scroll=True
    )

    # Contenedor para la imagen
    image_container = ft.Container(
        content=None,
        width=600,
        height=400,
        bgcolor="black",
        border_radius=10,
        alignment=ft.alignment.center
    )

    # Función que responde al cambio en el menú de selección
    def on_menu_change(e):
        search_type = menu.value
        if search_type:
            # Ejecutar el script correspondiente y obtener la salida y la ruta de la imagen
            output, image_path = run_app_py(search_type)

            # Agregar los resultados al ListView sin eliminar los anteriores
            list_view.controls.append(ft.Text(f"Resultados de {search_type}:", color="white"))
            list_view.controls.append(ft.Text(output, color="white"))

            # Verificar si la imagen fue generada correctamente y mostrarla
            if os.path.exists(image_path):
                image = ft.Image(src=image_path, width=int(600 * zoom_level), height=int(400 * zoom_level))
                image_container.content = image  # Actualizar el contenedor de la imagen
            else:
                list_view.controls.append(ft.Text("No se pudo cargar la imagen.", color="red"))

            page.update()

    # Funciones para zoom
    def zoom_in(e):
        nonlocal zoom_level
        zoom_level *= 1.2  # Aumentar el nivel de zoom
        update_image_size()

    def zoom_out(e):
        nonlocal zoom_level
        zoom_level /= 1.2  # Reducir el nivel de zoom
        update_image_size()

    def update_image_size():
        if image_container.content:
            image = image_container.content
            image.width = int(600 * zoom_level)
            image.height = int(400 * zoom_level)
            page.update()

    # Botones para zoom
    zoom_in_button = ft.IconButton(ft.icons.ADD, on_click=zoom_in, tooltip="Zoom In")
    zoom_out_button = ft.IconButton(ft.icons.REMOVE, on_click=zoom_out, tooltip="Zoom Out")

    # Asignar la función de cambio al menú
    menu.on_change = on_menu_change

    # Añadir todos los controles a la página
    page.add(
        ft.Row(
            controls=[panel_menu, list_view],
            alignment=ft.MainAxisAlignment.START,
        ),
        ft.Row(
            controls=[
                image_container,
                ft.Column(
                    controls=[zoom_in_button, zoom_out_button],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
