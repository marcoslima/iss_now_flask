from abc import ABC, abstractmethod
import logging
from typing import List

from iss_kml.domain.basic_domain import BasicEntity


class BasicPersistAdapter(ABC):
    def __init__(self, adapted_class, logger=None):
        """
        Adapter para persistencia de um entity
        :param adapted_class: Classe sendo adaptada
        """
        self._class = adapted_class
        self._logger = logger if logger else logging.getLogger()

    @property
    def logger(self):
        return self._logger

    @property
    def adapted_class(self):
        return self._class

    @property
    def adapted_class_name(self):
        return self._class.__name__

    @abstractmethod
    def list_all(self):
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, item_id):
        raise NotImplementedError

    @abstractmethod
    def save(self, serialized_data):
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id):
        raise NotImplementedError

    @abstractmethod
    def save_many(self, entity_list: List[BasicEntity]):
        raise NotImplementedError

    @abstractmethod
    def delete_many(self, entity_ids: List[str]):
        raise NotImplementedError

    @staticmethod
    def filter_and(*args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def filter_or(*args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def filter(self, *args, **kwargs):
        """
        Filtra objetos de acordo com o critério especificado.
        Para especificar o critérios, que por default são concatenados
        com o operador lógico *ou*, use o nome do campo junto com o operador
        desejado concatenado com um "__" (duplo sublinha).

        Exemplo: Para filtrar todos os objetos em que o campo email seja
        igual à "nome@dom.com", o filtro deverá ser chamado assim:

.. code-block:: python

            result = adapter.filter(email__eq="nome@dom.com")


        Para usar o operador lógico *and*, use o método filter_and.

        Exemplo: Para filtrar todos os objetos em que o campo email seja
        igual à "nome@dom.com" e tenha o saldo menor que 1000, faça assim:

.. code-block:: python

            result = adapter.filter(
                adapter.filter_and(email__eq="nome@dom.com", saldo__lt=1000))

Um exmeplo mais complexo
------------------------

(a=1 or b=2) and (c=3 or (d=4 and e=5)) pode-se fazer assim:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    _and = BasicPersistAdapter.filter_and
    _or = BasicPersistAdapter.filter_or
    result = adapter.filter(_and(_or(a__eq=1, b__eq=2),
        _or(_and(d__eq=4, e__eq=5), c__eq=3)))

:raises ValueError(Comparador inválido): se o comparador especificado
    não for um dos seguintes:
       [begins_with, between, contains, eq, exists, gt, gte, is_in, lt,
        lte, ne, not_exists]

:return: Lista de objetos
        """
        raise NotImplementedError

    @abstractmethod
    def lock_row(self, entity_id):
        """
        Locks a row for update until release_row is called with same entity_id
        :param entity_id: ID of row to be locked
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def release_row(self, entity_id):
        """
        Releases a row locked by lock_row
        :param entity_id:
        :return:
        """
        raise NotImplementedError
