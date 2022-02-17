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
