import os
import shutil
import winreg

import gdown


class GameSettingsManager:
    def __init__(self, game_folder: str, possible_dirs: list[str]) -> None:
        self.game_folder = game_folder
        self.possible_dirs = possible_dirs


    def find_game_folder(self) -> str | None:

        print("Searching game folder..")

        drives = [chr(x) + ":/" for x in range(65, 91) if os.path.exists(chr(x) + ":")]

        for drive in drives:
            for root in self.possible_dirs:
                try:
                    new_root = os.path.join(drive, root)
                    directory = os.listdir(new_root)
                except FileNotFoundError:
                    pass
                else:
                    if self.game_folder in directory:
                        print(f"Game directory was found in {new_root}")
                        return os.path.join(new_root, self.game_folder)

        for drive in drives:
            for root, dirs, files in os.walk(drive):
                if self.game_folder in dirs:
                    new_root = os.path.join(drive, root)
                    print(f"Game directory was found in {new_root}")
                    return os.path.join(new_root, self.game_folder)

    @staticmethod
    def extract_settings(settings_root: str) -> tuple[str, dict]:
        with open(settings_root, "r", encoding="utf-16le") as file:
            settings = [line.strip() for line in file][2:]
            root = settings[0].strip("[]")[18:]
            regedit_settings = {}
            for setting in settings[1:]:
                setting_name, setting_value = setting.split("=dword:")
                setting_name = setting_name.strip('"')
                setting_value = int(setting_value, 16)

                regedit_settings[setting_name] = setting_value

        return root, regedit_settings

    @staticmethod
    def apply_settings(game_path: str, settings: dict[str, int]) -> None:
        root = winreg.HKEY_CURRENT_USER

        try:
            key = winreg.OpenKeyEx(root, game_path, 0, winreg.KEY_ALL_ACCESS)
        except FileNotFoundError:
            raise FileNotFoundError("Game is not installed on your computer.")

        for name, value in settings.items():
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)

        if key:
            winreg.CloseKey(key)

    @staticmethod
    def download_settings(game_folder: str) -> str:
        url = input("Please enter url to google drive\n")
        link_id = url.split("=")[-1]

        gdown.download(id=link_id)

        try:
            shutil.move("settings.reg", game_folder)
        except:
            print("Settings file already exists in the game folder")

        settings_root = os.path.join(game_folder, "settings.reg")

        return settings_root

    @staticmethod
    def start_game(game_folder: str) -> None:
        game_exe = os.path.join(game_folder, "Goose Goose Duck")
        os.startfile(game_exe)


    def main(self) -> None:
        game_folder = self.find_game_folder()

        if game_folder:
            settings_root = self.download_settings(game_folder)
            path, settings = self.extract_settings(settings_root)
            self.apply_settings(path, settings)
            self.start_game(game_folder)
        else:
            print("Sorry, game folder was not found")


if __name__ == "__main__":
    game_manager = GameSettingsManager(
        game_folder="Goose Goose Duck",
        possible_dirs=[
            "\games",
            "\игры",
            "\steam\steamapps\common",
            "\games\steam\steamapps\common",
            "\игры\steam\steamapps\common",
            "\стим\steam\steamapps\common",
        ],
    )

    game_manager.main()
