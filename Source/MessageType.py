from enum import Enum


class MessageType(Enum):
    Login = 1,
    Register = 2,
    Bid = 3,
    Join = 4,
    Leave = 5,
    Create = 6,
    Quit = 7,
    GetLobbies = 8
    RefreshTable = 9
    StartTable = 10
    RefreshTableForOne = 11
