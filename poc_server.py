import gzip
from io import BytesIO
from pywinauto import Desktop
from flask import Flask, Response, request


class ScrShrServer:
    def __init__(self):
        self.__app = Flask(__name__)
        self.__shared_window = ScrShrServer.select_desktop_window()

        self.__route_screen_image()
        self.__route_client_page()
        self.__compress_res()

    def run(self):
        self.__app.run(host='0.0.0.0')

    def __compress_res(self):
        @self.__app.after_request
        def compress_response(response):
            if 'gzip' in request.headers.get('Accept-Encoding', ''):
                compressed_data = gzip.compress(response.data)
                response.set_data(compressed_data)

                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Content-Length'] = len(compressed_data)

            return response

    def __route_screen_image(self):
        @self.__app.route(f'/current_screen_image')
        def serve_window_image():
            winimg = self.__shared_window.capture_as_image()
            jpg_bytes_stream = BytesIO()

            winimg.save(jpg_bytes_stream, format='JPEG')
            jpg_bytes_stream.seek(0)

            return Response(jpg_bytes_stream, mimetype='image/jpeg')

    def __route_client_page(self):
        @self.__app.route(f'/')
        def serve_index_page():
            return \
'''
<!DOCTYPE html>
<html>
    <body>
        <img id="window_image" /> <br />

        <label for="update_screen_interval">Choose update-rate (20 to 0.2 fps): </label>
        <input type="range" id="update_screen_interval" min="50" max="5000" oninput="resetUpdateInterval(this.value);" />

        <br /> <text id="current_interval_rate"></text>

        <script>
        var update_screen_image_timer = null;

        function updateImage() {
            const timestamp = new Date().getTime();
            window_image.src = `current_screen_image?timestamp=${timestamp}`;
        }

        function resetUpdateInterval(new_interval_value)
        {
            clearInterval(update_screen_image_timer);
            update_screen_interval.value = new_interval_value;

            update_screen_image_timer = setInterval(updateImage, new_interval_value);
            current_interval_rate.innerText = (1000 / new_interval_value).toFixed(3) + " fps";
        }

        resetUpdateInterval(200);
        </script>
    </body>
</html>
'''

    @staticmethod
    def captures_generator(shared_window):
        while True:
            window_image = shared_window.capture_as_image()
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
    server = ScrShrServer()
    server.run()


if __name__ == '__main__':
    main()
