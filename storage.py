import json
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from dateutil.relativedelta import relativedelta


class BaseStorage(ABC):
    @abstractmethod
    def create_tour(self, tour: dict):
        pass

    @abstractmethod
    def get_tour(self, skip: int = 0, limit: int = 10, search: str = ''):
        pass

    @abstractmethod
    def get_info_tour(self, tour_id: str):
        pass

    @abstractmethod
    def delete_tour(self, tour_id: str):
        pass

    @abstractmethod
    def update_tour(self, tour_id: str, country: str):
        pass


class JSONStorage(BaseStorage):
    def __init__(self):
        self.file_name = 'storage.json'
        my_file = Path(self.file_name)
        if not my_file.is_file:
            with open(self.file_name, mode='w', encoding='utf-8') as file:
                json.dump([], file, indent=4)

    def create_tour(self, tour: dict):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)
        tour['id'] = uuid4().hex
        content.append(tour)
        with open(self.file_name, mode='w', encoding='utf') as file:
            json.dump(content, file, indent=4)

    def get_tour(self, skip: int = 0, limit: int = 10, search: str = ''):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)
        if search:
            data = []
            for tour in content:
                if search in tour['country']:
                    data.append(tour)
            sliced = data[skip:][:limit]
            return sliced
        sliced = content[skip:][:limit]
        return sliced

    def get_info_tour(self, tour_id: str):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)
        for tour in content:
            if tour_id == tour['id']:
                return tour
        return {}

    def delete_tour(self, tour_id: str):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)
        was_found = False
        for tour in content:
            if tour_id == tour['id']:
                content.remove(tour)
                was_found = True
                break
        if was_found:
            with open(self.file_name, mode='w', encoding='utf') as file:
                json.dump(content, file, indent=4)
        raise ValueError()
    def update_tour(self, tour_id: str, country: str):
        with open(self.file_name, mode='r') as file:
            content: list[dict] = json.load(file)
        was_found = False
        for tour in content:
            if tour_id == tour['id']:
                tour['country'] = country
                was_found = True
                break
        if was_found:
            with open(self.file_name, mode='w', encoding='utf') as file:
                json.dump(content, file, indent=4)
        raise ValueError()

today = datetime.now()
future_date = today + relativedelta(months=2)

storage = JSONStorage()
tour = {'country': 'Greece', 'date': '3.01.2025', 'duration': '2 weeks'}
# storage.create_tour(tour)
pass
