from semver import VersionInfo

from .exceptions import QuestLoadError

VERSION_KEY = "_version"

def semver_safe(start: VersionInfo, dest: VersionInfo) -> bool:
    """ whether semver loading is going to be safe """
    if start.major != dest.major:
        return False

    # check it's not a downgrade of minor version
    if start.minor > dest.minor:
        return False
    
    return True

class Quest:
    def __init__(self, version: str, quest_data: dict):
        self.semver = VersionInfo.parse(version)
        self.quest_data = quest_data

    def load(self, save_data: dict) -> None:
        """ Load save data back into structure """

        # check save version is safe before upgrading
        save_semver = VersionInfo.parse(save_data[VERSION_KEY])
        if not semver_safe(save_semver, self.semver):
            raise QuestLoadError(f"Unsafe version mismatch! {save_semver} -> {self.semver}")

        self.quest_data.update(save_data)

    def update_save_data(self) -> dict:
        """ Updates save data with new version and output """

        self.quest_data[VERSION_KEY] = self.semver
        return self.quest_data
