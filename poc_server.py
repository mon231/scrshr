from pywinauto import Desktop


def get_shareable_windows(desktop : Desktop):
    return list(filter(
        lambda window: (
            window.is_visible() and
            window.is_keyboard_focusable() and
            window.element_info.name
        ),
        desktop.windows()
    ))


def select_shareable_window(desktop: Desktop):
    shareable_windows = get_shareable_windows(desktop)
    print('Choose a window to share from the list below:')

    for i in range(len(shareable_windows)):
        print(f'{i + 1}. {shareable_windows[i].element_info.name}')

    return shareable_windows[int(input('Enter window number: ')) + 1]


def share_window(window):
    while True:
        window_image = window.capture_as_image()
        # TODO: send to clients (?)


def main():
    current_desktop = Desktop(backend="uia")
    window_to_share = select_shareable_window(current_desktop)


if __name__ == '__main__':
    main()
