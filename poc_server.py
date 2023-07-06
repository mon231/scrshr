import gzip # TODO: gzip the http data (?)
import PIL.Image as Image
from pywinauto import Desktop
from flask import Flask, Response


class ScrShrServer:
    def __init__(self, server_name: str = __name__):
        self.__app = Flask(server_name)
        self.__shared_window = ScrShrServer.select_desktop_window()

        @self.__app.route('/')
        def mymethod():
            return Response(
                ScrShrServer.captures_generator(self.__shared_window),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )

        self.__app.run()

    @staticmethod
    def captures_generator(shared_window):
        while True:
            window_image: Image = shared_window.capture_as_image()
            img_bytes = window_image.tobytes()

            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' +
                img_bytes +
                b'\r\n'
            )

    @staticmethod
    def select_desktop_window():
        current_desktop = Desktop(backend="uia")
        return ScrShrServer.select_shareable_window(current_desktop)

    @staticmethod
    def get_shareable_windows(desktop : Desktop):
        return list(filter(
            lambda window: (
                window.is_visible() and
                window.is_keyboard_focusable() and
                window.element_info.name
            ),
            desktop.windows()
        ))

    @staticmethod
    def select_shareable_window(desktop: Desktop):
        shareable_windows = ScrShrServer.get_shareable_windows(desktop)
        print('Choose a window to share from the list below:')

        for i in range(len(shareable_windows)):
            print(f'{i + 1}. {shareable_windows[i].element_info.name}')

        return shareable_windows[int(input('Enter window number: ')) - 1]


def main():
    ScrShrServer('mysrvr')


if __name__ == '__main__':
    main()
