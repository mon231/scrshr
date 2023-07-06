import io
import gzip # TODO: gzip the http data (?)
import PIL.Image as Image
from pywinauto import Desktop
from flask import Flask, Response


class ScrShrServer:
    def __init__(self, server_name: str = __name__):
        self.__app = Flask(server_name)
        self.__shared_window = ScrShrServer.select_desktop_window()

        @self.__app.route('/current_screen_image')
        def mymethod():
            winimg = self.__shared_window.capture_as_image()
            jpg_bytes_stream = io.BytesIO()

            winimg.save(jpg_bytes_stream, format='JPEG')
            jpg_bytes_stream.seek(0)

            return Response(jpg_bytes_stream, mimetype='image/jpeg')

        @self.__app.route('/')
        def x():
            return \
'''
<!DOCTYPE html>
<html>
    <body>
        <img id="window_image" src="myimg.jpg" />
        <script>
        const img = document.getElementById('window_image');

        function updateImage() {
            const timestamp = new Date().getTime();
            img.src = `current_screen_image?timestamp=${timestamp}`;
        }

        setInterval(updateImage, 1000);
        </script>
    </body>
</html>
'''

        self.__app.run()

    @staticmethod
    def captures_generator(shared_window):
        while True:
            window_image: Image = shared_window.capture_as_image()
            yield window_image.tobytes()

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
