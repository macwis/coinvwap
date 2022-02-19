from collections import deque
from typing import Dict, List


class VWAPStore:
    """
    Storage for the 200 data points and computation of VWAP indicator.
    """

    def __init__(
        self,
        product_ids: List[str],
        price_field: str,
        quantity_field: str,
        type_field: str = "ticker",
    ) -> None:
        self.product_ids = product_ids
        self.price_field = price_field
        self.quantity_field = quantity_field
        self.prices_n_vols = {
            product_id: deque(maxlen=200) for product_id in product_ids
        }
        self.type_field = type_field

    def store(self, payload: Dict) -> None:
        if payload["type"] == self.type_field:
            self._put(
                payload["product_id"],
                float(payload[self.price_field]),
                float(payload[self.quantity_field]),
            )

    def _put(self, product_id: str, price: float, last_size: float) -> None:
        if (
            product_id
            in self.prices_n_vols.keys()  # pylint: disable=consider-iterating-dictionary
        ):
            self.prices_n_vols[product_id].append((price, last_size))
        else:
            # TODO: more pro exception handling to be added
            pass

    @staticmethod
    def vwap(prices: List[float], quantity: List[float]) -> float:
        if len(quantity) == 0:
            return 0.0
        return sum([pj * qj for pj, qj in zip(prices, quantity)]) / sum(quantity)

    @staticmethod
    def vwap_formated(prices: List[float], vols: List[float]):
        return f"{VWAPStore.vwap(prices, vols):010f}"

    def report(self, point_counts=False) -> str:
        buff = ""
        for product_id, product_item in self.prices_n_vols.items():
            prices = [val[0] for val in product_item]
            vols = [val[1] for val in product_item]
            buff += f"{product_id}\t{VWAPStore.vwap_formated(prices, vols)}"
            if point_counts:
                buff += f"\tpoints:\t{len(product_item)}"
            buff += "\n"
        return buff


class VWAPStoreFast:  # pylint: disable=too-many-instance-attributes
    """
    Storage for the 200 data points and computation of VWAP indicator.
    """

    def __init__(
        self,
        product_ids: List[str],
        price_field: str,
        quantity_field: str,
        type_field: str = "ticker",
    ) -> None:
        self.product_ids = product_ids
        self.price_field = price_field
        self.quantity_field = quantity_field
        self.prices_n_vols = {product_id: [] for product_id in product_ids}
        self.sum_of_pjqj = {product_id: 0.0 for product_id in product_ids}
        self.sum_of_qj = {product_id: 0.0 for product_id in product_ids}
        self.count_of_j = 0
        self.type_field = type_field

    def store(self, payload: Dict) -> None:
        if payload["type"] == self.type_field:
            self._put(
                payload["product_id"],
                float(payload[self.price_field]),
                float(payload[self.quantity_field]),
            )

    def _put(self, product_id: str, price: float, last_size: float) -> None:
        if self.count_of_j >= 200:
            # Remove the oldest
            self.sum_of_pjqj[product_id] -= (
                self.prices_n_vols[product_id][0][0]
                * self.prices_n_vols[product_id][0][1]
            )
            self.sum_of_qj[product_id] -= self.prices_n_vols[product_id][0][1]
            self.count_of_j -= 1
            del self.prices_n_vols[product_id][0]
        # Add the newest
        self.prices_n_vols[product_id].append((price, last_size))
        self.sum_of_pjqj[product_id] += price * last_size
        self.sum_of_qj[product_id] += last_size
        self.count_of_j += 1

    def vwap_fast(self, product_id):
        if self.sum_of_qj[product_id] == 0:
            return 0.0
        return self.sum_of_pjqj[product_id] / self.sum_of_qj[product_id]

    def vwap_formated(self, product_id):
        return f"{self.vwap_fast(product_id):010f}"

    def report(self, point_counts=False) -> str:
        buff = ""
        for product_id, product_item in self.prices_n_vols.items():
            buff += f"{product_id}\t{self.vwap_formated(product_id)}"
            if point_counts:
                buff += f"\tpoints:\t{len(product_item)}"
            buff += "\n"
        return buff
