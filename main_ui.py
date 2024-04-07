import flet as ft
import export
import steamReq


async def main_ui(page: ft.Page):
    page.title = "Парсер данных прользователей steam по нику"
    page.window_height = 400
    page.window_width = 500

    capsCheck = ft.Checkbox(label="Учитывать регистр", value=False, visible=False)

    async def vcc(e):
        capsCheck.visible = fullCheck.value
        page.update()

    fullCheck = ft.Checkbox(label="Полное совпадение", value=False, on_change=vcc)
    row = ft.Row(spacing=20, controls=[fullCheck, capsCheck])
    page.add(row)

    inp = ft.TextField(value="", width=400, height=50)
    page.add(inp)

    t = ft.Text(value="Ожидание пользователя", color="green")

    async def button_click(e):
        t.value = f'Сбор данных по запросу "{inp.value}"'
        page.update()
        cookies = await steamReq.getSessionId()
        nLinks = await steamReq.getLinksFromSteam(inp.value, cookies, match=int(fullCheck.value) + int(capsCheck.value))
        t.value = f'Данные({nLinks}) сохранены в папке out в таблице "{export.safeName(inp.value)}.xlsx" в папке "{export.pathOut}"'
        page.update()

    btn = ft.ElevatedButton("Поиск", on_click=button_click)
    page.add(btn)
    page.add(t)


if __name__ == '__main__':
    ft.app(target=main_ui)
