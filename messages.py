from abc import ABC, abstractmethod


class MessageProvider(ABC):

    @abstractmethod
    def start_message(self) -> str:
        pass

    @abstractmethod
    def help_message(self) -> str:
        pass

    @abstractmethod
    def invalid_temperature_type(self) -> str:
        pass

    @abstractmethod
    def temperature_bounds(self) -> str:
        pass

    @abstractmethod
    def temperature_set(self, value: float) -> str:
        pass

    @abstractmethod
    def invalid_length_type(self) -> str:
        pass

    @abstractmethod
    def length_bounds(self) -> str:
        pass

    @abstractmethod
    def length_set(self, value: int) -> str:
        pass

    @abstractmethod
    def default_message(self, temp: float, length: int):
        pass

    @abstractmethod
    def message_bounds(self) -> str:
        pass

    @abstractmethod
    def filtered_message_bounds(self, filtered: str):
        pass


class CommonMessageProvider(MessageProvider):
    def start_message(self) -> str:
        return "Здравствуй, напиши мне что-нибудь, а я продолжу."

    def invalid_temperature_type(self) -> str:
        pass

    def temperature_bounds(self) -> str:
        pass

    def temperature_set(self, value: float) -> str:
        pass

    def invalid_length_type(self) -> str:
        pass

    def length_bounds(self) -> str:
        pass

    def length_set(self, value: int) -> str:
        pass

    def default_message(self, temp: float, length: int):
        pass

    def message_bounds(self) -> str:
        pass

    def filtered_message_bounds(self, filtered: str):
        pass