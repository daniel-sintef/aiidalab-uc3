from pathlib import Path
from typing import TYPE_CHECKING

from setuptools import setup

if TYPE_CHECKING:
    from typing import Optional, Union


def gitlab_token(source: "Optional[Union[Path, str]]" = None) -> str:
    """Retrieve the Fraunhofer GitLab Project Access Token"""
    token_file_location = (
        Path(source).resolve()
        if source
        else Path(__file__).resolve().parent / ".mp_gitlab_token"
    )
    if not token_file_location.exists():
        raise FileNotFoundError(
            f"Could not find file ({token_file_location}) containing the Fraunhofer "
            "GitLab Project Access Token !"
        )
    return token_file_location.read_text(encoding="utf8").strip()


setup(
    install_requires=(
        [
            f"aiida-marketusercase3 @ git+https://github.com/daniel-sintef/aiida-marketusercase3.git@master",
            "aiida-core~=2.1,<3",
            "aiidalab>=21.09.0",
            "aiidalab-widgets-base==2.0.0b1",
        ]
    )
)
