import flet as ft
import subprocess

def run_app_py(search_type):
    try:
        search_type_map = {
            "Búsqueda por Anchura": "anchura",
            "Búsqueda por Profundidad": "profundidad",
            "Búsqueda por Profundidad Iterativa": "profundidad_iterativa",
            "Búsqueda Bidireccional": "bidireccional",
        }
        search_type_argument = search_type_map.get(search_type, "anchura")

        result = subprocess.run(
            ['python', 'app.py', search_type_argument],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error ejecutando app.py: {e.stderr}"

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
            output = run_app_py(search_type)
            list_view.controls = [
                ft.Text(f"Resultados de {search_type}:", color="white"),
                ft.Text(output, color="white"),
            ]
            page.update()

    menu.on_change = on_menu_change

    page.add(
        ft.Row(
            controls=[
                panel_menu,
                list_view
            ],
            alignment=ft.MainAxisAlignment.START,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
